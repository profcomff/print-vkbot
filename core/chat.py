# Marakulin Andrey @annndruha
# 2021
import os
import logging
import time
import traceback
import requests

import core.answers as ru
import func.vkontakte_functions as vk
import core.keybords as kb

PDF_PATH = "pdf"


def get_attachments(user):
    if len(user.attachments) > 1:
        vk.write_msg(user.user_id, "Файлов слишком много. Прикрепите только один файл pdf.")
        return False
    if user.attachments[0]['type'] != 'doc':
        vk.write_msg(user.user_id, "Я умею печатать только документы в формате pdf.")
        return False
    else:
        ext = user.attachments[0]['doc']['ext']
        if ext != 'pdf':
            vk.write_msg(user.user_id, "Я умею печатать только документы в формате pdf.")
            return False
        title = user.attachments[0]['doc']['title']
        url = user.attachments[0]['doc']['url']

        if not os.path.exists(PDF_PATH):
            os.makedirs(PDF_PATH)
        if not os.path.exists(os.path.join(PDF_PATH, str(user.user_id))):
            os.makedirs(os.path.join(PDF_PATH, str(user.user_id)))

        r = requests.get(url, allow_redirects=True)
        with open(os.path.join(PDF_PATH, str(user.user_id), title), 'wb') as f:
            f.write(r.content)
        vk.write_msg(user.user_id, "Вложения получены успешно")
        return True


def order_print(user, requisites=None):
    if get_attachments(user):
        vk.write_msg(user.user_id, "Попытка заказать печать")

    # r = requests.post('https://app.profcomff.com/print', data={'surname': 'value',
    #                                                            'number': user.last_name,
    #                                                            'filename': 'test'})
    # logging.info(r)


# TODO: Validate number and remember or help
def validate_proff(user):
    vk.write_msg(user.user_id, "Проверка профномера и сохранение в базу.")


# TODO: Check number in base and print
def check_proff(user):
    vk.write_msg(user.user_id, "Проверка номера в базе.")


def message_analyzer(user):
    try:
        if len(user.message) <= 0 and len(user.attachments) == 0:
            kb.main_page(user.user_id, ru.kb_ans['help'])
        elif len(user.message) > 0 and len(user.attachments) == 0:
            validate_proff(user)
        elif len(user.message) <= 0 and len(user.attachments) > 0:
            check_proff(user)
            order_print(user)
        elif len(user.message) > 0 and len(user.attachments) > 0:
            validate_proff(user)
            order_print(user)

    except OSError as err:
        raise err
    except BaseException as err:
        ans = ru.errors['im_broken']
        vk.write_msg(user.user_id, ans)
        logging.error("Unknown Exception (message_analyzer), description:")
        traceback.print_tb(err.__traceback__)
        logging.error(str(err.args))


def process_event(event):
    if event.type == vk.VkBotEventType.MESSAGE_NEW:
        vk_user = vk.user_get(event.message['from_id'])
        user = vk.User(event.message['from_id'], event.message['text'],
                       event.message.attachments, (vk_user[0])['first_name'], (vk_user[0])['last_name'])

        if hasattr(event, 'payload'):
            kb.keyboard_browser(user, event.payload)
        else:
            message_analyzer(user)

    if event.type == vk.VkBotEventType.MESSAGE_EVENT:
        vk_user = vk.user_get(event.message['from_id'])
        user = vk.User(event.message['from_id'], event.message['text'],
                       event.message.attachments, (vk_user[0])['first_name'], (vk_user[0])['last_name'])
        vk.write_msg(user.user_id, "Calback обработан")


def chat_loop():
    while True:
        try:
            vk.reconnect()
            for event in vk.longpoll.listen():
                process_event(event)

        except OSError as err:
            logging.error("OSError (longpull_loop), description:")
            traceback.print_tb(err.__traceback__)
            logging.error(str(err.args))
            try:
                logging.warning("Try to recconnect VK...")
                vk.reconnect()
                logging.info("VK connected successful")
                time.sleep(1)
            except:
                logging.error("Recconnect VK failed")
                time.sleep(10)

        except BaseException as err:
            logging.error("BaseException (longpull_loop), description:")
            traceback.print_tb(err.__traceback__)
            logging.error(str(err.args))
            time.sleep(5)

        except:
            logging.error("Something go wrong. (chat_loop)")
