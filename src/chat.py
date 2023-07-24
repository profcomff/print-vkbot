# Marakulin Andrey @annndruha
# 2021

import json
import logging
import os
import traceback

import psycopg2
import requests
from sqlalchemy.exc import SQLAlchemyError
from vk_api.exceptions import VkApiError

import src.keybords as kb
import src.marketing as marketing
import src.vk as vk
from src.auth import check_auth
from src.db import VkUser, reconnect_session, session
from src.settings import Settings
from src.answers import Answers

settings = Settings()
ans = Answers()


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            vk.reconnect()
            reconnect_session()
            func(*args, **kwargs)
        except OSError as err:
            logging.error('OSError (longpull_loop), description:')
            logging.error(err)
            traceback.print_tb(err.__traceback__)
            try:
                logging.warning('Try to reconnect VK...')
                vk.reconnect()
                logging.warning('VK connected successful')
            except VkApiError:
                logging.error('Reconnect VK failed')

        except (SQLAlchemyError, psycopg2.Error) as err:
            logging.error('Database Error (longpull_loop), description:')
            logging.error(err)
            traceback.print_tb(err.__traceback__)
            try:
                logging.warning('Try to reconnect database...')

            except psycopg2.Error:
                logging.error('Reconnect database failed')
        except json.decoder.JSONDecodeError as err:
            # vk.send(user, ans.print_err)
            logging.error('JSONDecodeError (message_analyzer), description:')
            traceback.print_tb(err.__traceback__)
            logging.error(err)
        except Exception as err:
            logging.error('BaseException (longpull_loop), description:')
            traceback.print_tb(err.__traceback__)
            logging.error(err)
    return wrapper


@error_handler
def event_loop():
    for event in vk.longpoll.listen():
        if event.type != vk.VkBotEventType.MESSAGE_NEW:
            return

        user = vk.EventUser(event)
        if event.message.payload is not None:
            kb.keyboard_browser(user, event.message.payload)
        else:
            message_analyzer(user)


def message_analyzer(user: vk.EventUser):
    # Define type of message: help, update requisites, file
    if len(user.message) > 0 and len(user.attachments) == 0:
        for word in ans.ask_help:
            if word in user.message.lower():
                kb.main_page(user)
                return
        register_bot_user(user)
        return

    requisites = check_auth(user)
    if requisites is None:
        vk.send(user, ans.val_need)
        vk.send(user, ans.exp_name)
        return

    order_print(user, requisites)


def get_attachments(user: vk.EventUser):
    if len(user.attachments) > 1:
        vk.send(user, ans.many_files)
        marketing.print_exc_many(
            file_count=len(user.attachments),
            vk_id=user.user_id,
        )
        return
    if user.attachments[0]['type'] != 'doc':
        vk.send(user, ans.only_pdfs)
        marketing.print_exc_format(
            file_ext='image',
            vk_id=user.user_id,
        )
        return
    if user.attachments[0]['type'] == 'doc':
        ext = user.attachments[0]['doc']['ext']
        if ext not in ['pdf', 'PDF']:
            vk.send(user, ans.only_pdfs)
            marketing.print_exc_format(
                file_ext=len(user.attachments[0]['doc']['ext']),
                vk_id=user.user_id,
            )
            return
        title = user.attachments[0]['doc']['title']
        url = user.attachments[0]['doc']['url']

        if not os.path.exists(settings.PDF_PATH):
            os.makedirs(settings.PDF_PATH)
        if not os.path.exists(os.path.join(settings.PDF_PATH, str(user.user_id))):
            os.makedirs(os.path.join(settings.PDF_PATH, str(user.user_id)))

        r = requests.get(url, allow_redirects=True)
        with open(os.path.join(settings.PDF_PATH, str(user.user_id), title), 'wb') as f:
            f.write(r.content)
        vk.send(user, ans.file_uploaded.format(title))
        return os.path.join(settings.PDF_PATH, str(user.user_id), title), title


def order_print(user: vk.EventUser, requisites):
    # Check user
    vk_id, surname, number = requisites

    path_title = get_attachments(user)
    pin = None
    if path_title is not None:
        pdf_path, title = path_title
        r = requests.post(settings.PRINT_URL + '/file', json={'surname': surname, 'number': number, 'filename': title})
        if r.status_code == 200:
            pin = r.json()['pin']
            files = {'file': (title, open(pdf_path, 'rb'), 'application/pdf', {'Expires': '0'})}
            rfile = requests.post(settings.PRINT_URL + '/file/' + pin, files=files)
            if rfile.status_code == 200:
                kb_qr = vk.VkKeyboard(inline=True)
                kb_qr.add_openlink_button(ans.qr_button_text, link=settings.PRINT_URL_QR + str(pin))
                vk.send(user, ans.send_to_print.format(pin), keyboard=kb_qr.get_keyboard())
                marketing.print_success(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                )
            elif rfile.status_code == 413:
                vk.send(user, ans.file_size_err)
                marketing.print_exc_other(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                    status_code=rfile.status_code,
                    description='File is too big',
                )
            else:
                vk.send(user, ans.print_err)
                marketing.print_exc_other(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                    status_code=rfile.status_code,
                    description='Fail on file upload',
                )
        else:
            vk.send(user, ans.print_err)
            marketing.print_exc_other(
                vk_id=vk_id,
                surname=surname,
                number=number,
                pin=pin,
                status_code=r.status_code,
                description='Fail on fetching code',
            )


def register_bot_user(user: vk.EventUser):
    if len(user.message.split('\n')) == 2:
        surname = user.message.split('\n')[0].strip()
        number = user.message.split('\n')[1].strip()

        r = requests.get(settings.PRINT_URL + '/is_union_member', params=dict(surname=surname, v=1, number=number))
        data: VkUser | None = session.query(VkUser).filter(VkUser.vk_id == user.user_id).one_or_none()
        if r.json() and data is None:
            session.add(VkUser(vk_id=user.user_id, surname=surname, number=number))
            session.commit()
            vk.send(user, ans.val_pass)
            marketing.register(
                vk_id=user.user_id,
                surname=surname,
                number=number,
            )
            return True
        elif r.json() and data is not None:
            data.surname = surname
            data.number = number
            session.commit()
            vk.send(user, ans.val_update_pass)
            marketing.re_register(
                vk_id=user.user_id,
                surname=surname,
                number=number,
            )
            return True
        elif r.json() is False:
            vk.send(user, ans.val_fail)
            vk.send(user, ans.exp_name)
            marketing.register_exc_wrong(
                vk_id=user.user_id,
                surname=surname,
                number=number,
            )
    else:
        # TODO: check auth
        data: VkUser | None = session.query(VkUser).filter(VkUser.vk_id == user.user_id).one_or_none()
        if data is None:
            vk.send(user, ans.val_need)
            vk.send(user, ans.exp_name)
        else:
            vk.send(user, ans.val_update_fail)
            vk.send(user, ans.exp_name)
