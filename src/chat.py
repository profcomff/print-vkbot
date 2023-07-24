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
from src.auth import check_auth, check_union_member, add_user, update_user
from src.db import VkUser, reconnect_session, session
from src.settings import Settings
from src.answers import Answers

settings = Settings()
ans = Answers()


def event_loop():
    user = None
    try:
        vk.reconnect()
        reconnect_session()
        for event in vk.longpoll.listen():
            if event.type != vk.VkBotEventType.MESSAGE_NEW:
                return
    
            user = vk.EventUser(event)
            if event.message.payload is not None:
                kb.keyboard_browser(user, event.message.payload)
            else:
                message_analyzer(user)
    except (OSError, VkApiError) as err:
        vk.send(user, ans.err_vk)
        logging.error(err)
        traceback.print_tb(err.__traceback__)
    except (SQLAlchemyError, psycopg2.Error) as err:
        vk.send(user, ans.err_bd)
        logging.error(err)
        traceback.print_tb(err.__traceback__)
    except json.decoder.JSONDecodeError as err:
        vk.send(user, ans.err_kb)
        logging.error(err)
        traceback.print_tb(err.__traceback__)
    except Exception as err:
        vk.send(user, ans.err_fatal)
        logging.error(err)
        traceback.print_tb(err.__traceback__)


def message_analyzer(user: vk.EventUser):
    db_requisites = check_auth(user)
    # Если юзер прислал файл, проверим авторизацию
    if len(user.attachments) > 0:
        if db_requisites is None:
            vk.send(user, ans.val_need)
            vk.send(user, ans.val_name)
        else:
            order_print(user, db_requisites)
        return
    # Если юзер прислал текст, проверим не help ли это, если нет, то идём дальше
    if len(user.message) > 0:
        for word in ans.ask_help:
            if word in user.message.lower():
                kb.main_page(user)
                return
    # Если юзер прислал текст, но он не похож на обновление данных авторизации
    if len(user.message.split('\n')) != 2:
        if db_requisites is None:
            vk.send(user, ans.val_need)
            vk.send(user, ans.val_name)
        else:
            vk.send(user, ans.val_fail_format)
            vk.send(user, ans.val_name)
        return
    # Если юзер прислал текст, который похож на обновление данных авторизации
    if len(user.message.split('\n')) == 2:
        register_bot_user(user, db_requisites)
        return 
    # Если вообще непонятно что за сообщение пришло
    vk.send(user, ans.val_unknown_message)
    vk.send(user, ans.val_name)





def get_attachments(user: vk.EventUser):
    if len(user.attachments) > 1:
        vk.send(user, ans.warn_many_files)
        marketing.print_exc_many(
            file_count=len(user.attachments),
            vk_id=user.user_id,
        )
        return
    if user.attachments[0]['type'] != 'doc':
        vk.send(user, ans.warn_only_pdfs)
        marketing.print_exc_format(
            file_ext='image',
            vk_id=user.user_id,
        )
        return
    if user.attachments[0]['type'] == 'doc':
        ext = user.attachments[0]['doc']['ext']
        if ext not in ['pdf', 'PDF']:
            vk.send(user, ans.warn_only_pdfs)
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


def order_print(user: vk.EventUser, db_requisites):
    # Check user
    vk_id, surname, number = db_requisites

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
                vk.send(user, ans.warn_filesize)
                marketing.print_exc_other(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                    status_code=rfile.status_code,
                    description='File is too big',
                )
            else:
                vk.send(user, ans.err_print)
                marketing.print_exc_other(
                    vk_id=vk_id,
                    surname=surname,
                    number=number,
                    pin=pin,
                    status_code=rfile.status_code,
                    description='Fail on file upload',
                )
        else:
            vk.send(user, ans.err_print)
            marketing.print_exc_other(
                vk_id=vk_id,
                surname=surname,
                number=number,
                pin=pin,
                status_code=r.status_code,
                description='Fail on fetching code',
            )


def register_bot_user(user: vk.EventUser, db_requisites):
    surname = user.message.split('\n')[0].strip()
    number = user.message.split('\n')[1].strip()
    
    union_member = check_union_member(user, surname, number)

    # Если юзер не состоит в профсоюзе
    if union_member is None:
        vk.send(user, ans.val_fail)
        vk.send(user, ans.val_name)
        marketing.register_exc_wrong(
            vk_id=user.user_id,
            surname=surname,
            number=number,
        )
        return

    # Писать разные сообщения на первичное добавление в базу и на обновление данных
    if db_requisites is None:
        add_user(user, surname, number)
        vk.send(user, ans.val_pass)
        marketing.register(
            vk_id=user.user_id,
            surname=surname,
            number=number,
        )
    else:
        update_user(user, surname, number)
        vk.send(user, ans.val_update_pass)
        marketing.re_register(
            vk_id=user.user_id,
            surname=surname,
            number=number,
        )

