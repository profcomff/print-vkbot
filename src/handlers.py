# Marakulin Andrey @annndruha
# 2023

import json
import logging
import time

import psycopg2
import requests
from sqlalchemy.exc import SQLAlchemyError
from vk_api.bot_longpoll import VkBotEventType
from vk_api.exceptions import VkApiError

import src.auth as auth
import src.keybords as kb
import src.marketing as marketing
import src.vk as vk
from src.answers import ans
from src.settings import settings


def event_loop():
    longpoll = None
    while True:
        try:
            if longpoll is None:
                longpoll = vk.create_longpoll()
            events = longpoll.check()
        except (OSError, VkApiError, requests.RequestException, ValueError, KeyError) as err:
            logging.warning('VK Long Poll failed (%s). Retrying in 5 seconds.', type(err).__name__)
            time.sleep(5)
            continue

        for event in events:
            if event.type in (VkBotEventType.MESSAGE_NEW, VkBotEventType.MESSAGE_ALLOW):
                handle_event(event)


def handle_event(event):
    user = None
    try:
        user = vk.EventUser(event)
        if event.type == VkBotEventType.MESSAGE_ALLOW:
            kb.main_page(user)
        elif event.message.payload is not None:
            kb.keyboard_browser(user, event.message.payload)
        else:
            message_analyzer(user)
        return
    except VkApiError as err:
        logging.warning('VK API call failed (%s)', type(err).__name__)
        message = ans.err_vk
    except requests.RequestException as err:
        logging.warning('HTTP request while handling VK event failed (%s)', type(err).__name__)
        message = ans.err_print
    except (SQLAlchemyError, psycopg2.Error):
        logging.exception('VK user database operation failed')
        message = ans.err_bd
    except json.JSONDecodeError:
        logging.warning('Invalid VK keyboard payload')
        message = ans.err_kb
    except Exception:
        logging.exception('VK event handling failed')
        message = ans.err_fatal

    try:
        vk.send(user, message, keyboard=kb.links_keyboard())
    except (OSError, VkApiError, requests.RequestException) as err:
        logging.warning('Could not send the VK error reply (%s)', type(err).__name__)


def message_analyzer(user: vk.EventUser):
    db_requisites = auth.check(user)
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


def register_bot_user(user: vk.EventUser, db_requisites):
    surname = user.message.split('\n')[0].strip()
    number = user.message.split('\n')[1].strip()

    union_member = auth.check_union_member(user, surname, number)
    # Если юзер не состоит в профсоюзе
    if union_member is None:
        vk.send(user, ans.val_fail)
        vk.send(user, ans.val_name)
        marketing.register_exc_wrong(vk_id=user.user_id, surname=surname, number=number)
        return

    # Писать разные сообщения на первичное добавление в базу и на обновление данных
    if auth.check_user_in_db(user) is None:
        auth.add_user(user, surname, number)
        vk.send(user, ans.val_pass)
        marketing.register(vk_id=user.user_id, surname=surname, number=number)
    else:
        auth.update_user(user, surname, number)
        vk.send(user, ans.val_update_pass)
        marketing.re_register(vk_id=user.user_id, surname=surname, number=number)


def get_attachments(user: vk.EventUser):
    if len(user.attachments) > 1:
        vk.send(user, ans.warn_many_files)
        marketing.print_exc_many(file_count=len(user.attachments), vk_id=user.user_id)
        return

    if user.attachments[0]['type'] != 'doc':
        vk.send(user, ans.warn_only_pdfs)
        marketing.print_exc_format(file_ext='image', vk_id=user.user_id)
        return

    if user.attachments[0]['doc']['ext'] not in ['pdf', 'PDF']:
        vk.send(user, ans.warn_only_pdfs)
        marketing.print_exc_format(file_ext=len(user.attachments[0]['doc']['ext']), vk_id=user.user_id)
        return

    title = user.attachments[0]['doc']['title']
    url = user.attachments[0]['doc']['url']
    r = requests.get(url, timeout=(5, 30))
    r.raise_for_status()
    return r.content, title


def order_print(user: vk.EventUser, db_requisites):
    # Get user attachment
    file_content_title = get_attachments(user)
    if file_content_title is None:
        return

    # Get pin
    content, title = file_content_title
    vk_id, surname, number = db_requisites
    r = requests.post(
        settings.PRINT_URL + '/file',
        json={'surname': surname, 'number': number, 'filename': title, 'source': 'vkbot'},
        timeout=(5, 30),
    )

    # If get pin error
    if r.status_code != 200:
        vk.send(user, ans.err_print)
        marketing.print_exc_other(
            vk_id=vk_id, surname=surname, number=number, status_code=r.status_code, description='Fail on fetching code'
        )
        return

    # Upload file with pin
    pin = r.json()['pin']
    files = {'file': (title, content, 'application/pdf', {'Expires': '0'})}
    r = requests.post(settings.PRINT_URL + '/file/' + pin, files=files, timeout=(5, 30))

    # Send response
    if r.status_code == 200:
        vk.send(user, ans.send_to_print.format(title, pin), keyboard=kb.file_settings(pin))
        marketing.print_success(vk_id=vk_id, surname=surname, number=number, pin=pin)
    elif r.status_code == 413:
        vk.send(user, ans.warn_filesize)
        marketing.print_exc_other(
            vk_id=vk_id,
            surname=surname,
            number=number,
            pin=pin,
            status_code=r.status_code,
            description='File exceeds size or page limit',
        )
    elif r.status_code == 415:
        vk.send(user, ans.warn_unreadable_file)
        marketing.print_exc_other(
            vk_id=vk_id,
            surname=surname,
            number=number,
            pin=pin,
            status_code=r.status_code,
            description='Unsupported Media Type',
        )
    else:
        vk.send(user, ans.err_print)
        marketing.print_exc_other(
            vk_id=vk_id,
            surname=surname,
            number=number,
            pin=pin,
            status_code=r.status_code,
            description='Fail on file upload',
        )
