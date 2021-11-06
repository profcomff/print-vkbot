# Marakulin Andrey @annndruha
# 2021
import json
import logging
import traceback
import requests
import configparser

import core.answers as ru
import func.vkontakte_functions as vk
import func.database_functions as db


config = configparser.ConfigParser()
config.read('auth.ini')

# PDF_PATH = config["settings"]["pdf_path"]
# PRINT_URL = config["print_server"]["print_url"]
GET_MEMBER_URL = config["print_server"]["get_member_url"]


def main_page(user_id, ans="Главное меню", attach=None):
    kb = vk.VkKeyboard(one_time=False)

    kb.add_button("Инструкция", color='primary', payload=["command", "help"])
    vk.send_keyboard(user_id, kb.get_keyboard(), ans, attach=attach)


def check_auth(user_id):
    if db.get_user(user_id) is not None:
        _, surname, number = db.get_user(user_id)
        r = requests.get(GET_MEMBER_URL, params=dict(surname=surname, number=number, v=1))
        if r.json():
            return True
        else:
            return False
    else:
        return False


def auth_button(user_id, ans=""):
    kb = vk.VkKeyboard(inline=True)
    if check_auth(user_id):
        kb.add_button("Авторизовано", color='positive', payload=["command", "auth_true"])
    else:
        kb.add_button("Не авторизовано", color='negative', payload=["command", "auth_false"])

    vk.send_keyboard(user_id, kb.get_keyboard(), ans)


def keyboard_browser(user, str_payload):
    try:
        payload = json.loads(str_payload)
        if not isinstance(payload, list):
            main_page(user.user_id)
        if payload[0] == 'command':
            if payload[1] == 'auth_true':
                vk.write_msg(user.user_id, "Вы уже успешно авторизованы. Можете присылать файл на печать.")
            if payload[1] == 'auth_false':
                vk.write_msg(user.user_id, "Для использования принтера необходимо авторизоваться.\n"
                                           "Введите фамилию и номер профсоюзного билета в формате:")
                vk.write_msg(user.user_id, "Иванов\n1234567")
            if payload[1] == 'help':
                auth_button(user.user_id, ru.kb_ans['help'])

    except OSError as err:
        raise err
    except BaseException as err:
        ans = ru.errors['kb_error']
        vk.write_msg(user.user_id, ans)
        logging.error("Unknown Exception (keyboard_browser), description:")
        traceback.print_tb(err.__traceback__)
        logging.error(f"Unknown Exception (keyboard_browser), description: {str(err.args)}")
