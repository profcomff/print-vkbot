﻿# Marakulin Andrey @annndruha
# 2021
import os
import json
import logging
import time
import traceback

import requests
import psycopg2
from vk_api.exceptions import VkApiError

import src.answers as ru
import src.vkontakte_functions as vk
import src.database_functions as db
import src.marketing as log
import src.keybords as kb
from src.settings import Settings


settings = Settings()


def get_attachments(user):
    if len(user.attachments) > 1:
        vk.write_msg(user, ru.print_ans['many_files'])
        log.print_exc_many(
            file_count=len(user.attachments),
            vk_id=user.user_id,
        )
        return
    if user.attachments[0]['type'] != 'doc':
        vk.write_msg(user, ru.print_ans['only_pdfs'])
        log.print_exc_format(
            file_ext='image',
            vk_id=user.user_id,
        )
        return
    if user.attachments[0]['type'] == 'doc':
        ext = user.attachments[0]['doc']['ext']
        if ext != 'pdf':
            vk.write_msg(user, ru.print_ans['only_pdfs'])
            log.print_exc_format(
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
        vk.write_msg(user, ru.print_ans['file_uploaded'].format(title))
        return os.path.join(settings.PDF_PATH, str(user.user_id), title), title


def order_print(user, requisites):
    attstatus = get_attachments(user)
    vk_id, surname, number = requisites
    pin = None
    if attstatus is not None:
        pdf_path, title = attstatus
        r = requests.post(settings.PRINT_URL + '/file', json={'surname': surname, 'number': number, 'filename': title})
        if r.status_code == 200:
            pin = r.json()['pin']
            files = {'file': (title, open(pdf_path, 'rb'), 'application/pdf', {'Expires': '0'})}
            rfile = requests.post(settings.PRINT_URL + '/file/' + pin, files=files)
            if rfile.status_code == 200:
                kb_qr = vk.VkKeyboard(inline=True)
                kb_qr.add_openlink_button(ru.print_ans['qr_button_text'], link=settings.PRINT_URL_QR + str(pin))
                vk.send_keyboard(user, kb_qr.get_keyboard(), ru.print_ans['send_to_print'].format(pin))

                log.print(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                )
            elif rfile.status_code == 413:
                vk.write_msg(user, ru.errors['file_size_err'])
                log.print_exc_other(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                    status_code=rfile.status_code,
                    description='File is too big',
                )
            else:
                vk.write_msg(user, ru.errors['print_err'])
                log.print_exc_other(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                    status_code=rfile.status_code,
                    description='Fail on file upload',
                )
        else:
            vk.write_msg(user, ru.errors['print_err'])
            log.print_exc_other(
                vk_id=vk_id,
                surname=surname,
                number=number,
                pin=pin,
                status_code=r.status_code,
                description='Fail on fetching code',
            )


def validate_proff(user):
    if len(user.message.split('\n')) == 2:
        surname = user.message.split('\n')[0].strip()
        number = user.message.split('\n')[1].strip()

        r = requests.get(settings.PRINT_URL+'/is_union_member', params=dict(surname=surname, v=1, number=number))
        data = db.get_user(user.user_id)
        if r.json() and data is None:
            db.add_user(user.user_id, surname, number)
            kb.auth_button(user, ru.val_ans['val_pass'])
            log.register(
                vk_id=user.user_id,
                surname=surname,
                number=number,
            )
            return True
        elif r.json() and data is not None:
            db.update_user(user.user_id, surname, number)
            kb.auth_button(user, ru.val_ans['val_update_pass'])
            log.re_register(
                vk_id=user.user_id,
                surname=surname,
                number=number,
            )
            return True
        elif r.json() is False:
            vk.write_msg(user, ru.val_ans['val_fail'])
            vk.write_msg(user, ru.val_ans['exp_name'])
            log.register_exc_wrong(
                vk_id=user.user_id,
                surname=surname,
                number=number,
            )
    else:
        if db.get_user(user.user_id) is None:
            vk.write_msg(user, ru.val_ans['val_need'])
            vk.write_msg(user, ru.val_ans['exp_name'])
        else:
            vk.write_msg(user, ru.val_ans['val_update_fail'])
            vk.write_msg(user, ru.val_ans['exp_name'])


def check_proff(user):
    if db.get_user(user.user_id) is not None:
        vk_id, surname, number = db.get_user(user.user_id)
        r = requests.get(settings.PRINT_URL+'/is_union_member', params=dict(surname=surname, number=number, v=1))
        if r.json():
            return vk_id, surname, number
        else:
            vk.write_msg(user, ru.val_ans['val_need'])
            vk.write_msg(user, ru.val_ans['exp_name'])
    else:
        vk.write_msg(user, ru.val_ans['val_need'])
        vk.write_msg(user, ru.val_ans['exp_name'])


def message_analyzer(user):
    try:
        if len(user.message) > 0:
            for word in ru.ask_help:
                if word in user.message.lower():
                    kb.main_page(user)
                    kb.auth_button(user, links=True)
                    return

        if len(user.attachments) == 0:
            if len(user.message) > 0:
                validate_proff(user)
            else:
                kb.main_page(user)
                kb.auth_button(user, links=True)
        else:
            requisites = check_proff(user)
            if requisites is not None:
                order_print(user, requisites)

    except OSError as err:
        raise err
    except psycopg2.Error as err:
        vk.write_msg(user, ru.errors['bd_error'])
        raise err
    except json.decoder.JSONDecodeError as err:
        vk.write_msg(user, ru.errors['print_err'])
        logging.error('JSONDecodeError (message_analyzer), description:')
        logging.error(err)
        traceback.print_tb(err.__traceback__)
        time.sleep(1)
    except Exception as err:
        ans = ru.errors['im_broken']
        vk.write_msg(user, ans)
        logging.error('Unknown Exception (message_analyzer), description:')
        logging.error(err)
        traceback.print_tb(err.__traceback__)


def process_event(event):
    if event.type == vk.VkBotEventType.MESSAGE_NEW:
        vk_user = vk.user_get(event.message['from_id'])
        user = vk.User(event.message['from_id'], event.message['text'],
                       event.message.attachments, (vk_user[0])['first_name'], (vk_user[0])['last_name'])
        db.check_and_reconnect()
        if event.message.payload is not None:
            kb.keyboard_browser(user, event.message.payload)
        else:
            message_analyzer(user)


def chat_loop():
    while True:
        try:
            vk.reconnect()
            for event in vk.longpoll.listen():
                process_event(event)

        except OSError as err:
            logging.error('OSError (longpull_loop), description:')
            logging.error(err)
            traceback.print_tb(err.__traceback__)
            try:
                logging.warning('Try to recconnect VK...')
                vk.reconnect()
                logging.warning('VK connected successful')
                time.sleep(1)
            except VkApiError:
                logging.error('Recconnect VK failed')
                time.sleep(10)

        except psycopg2.Error as err:
            logging.error('Database Error (longpull_loop), description:')
            logging.error(err)
            traceback.print_tb(err.__traceback__)
            try:
                logging.warning('Try to recconnect database...')
                db.reconnect()
                logging.warning('Database connected successful')
                time.sleep(1)
            except psycopg2.Error:
                logging.error('Recconnect database failed')
                time.sleep(10)

        except Exception as err:
            logging.error('BaseException (longpull_loop), description:')
            traceback.print_tb(err.__traceback__)
            logging.error(err)
            time.sleep(5)
