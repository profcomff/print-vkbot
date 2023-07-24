# Marakulin Andrey @annndruha
# 2021
import json
import logging
import traceback

import psycopg2
import requests
from sqlalchemy.exc import SQLAlchemyError


import src.vkontakte_functions as vk
from src.db import VkUser, reconnect_session, session
from src.settings import Settings
from src.answers import Answers


settings = Settings()
ans = Answers()


def check_auth(user_id):
    data: VkUser | None = session.query(VkUser).filter(VkUser.vk_id == user_id).one_or_none()
    if data is not None:
        r = requests.get(url=settings.PRINT_URL + '/is_union_member',
                         params=dict(surname=data.surname, number=data.number, v=1))
        if r.json():  # TODO: Is correct?
            return True
    return False


def main_page(user, msg=ans.hey, attach=None):
    kb = vk.VkKeyboard(one_time=False)
    kb.add_button(ans.inst, color='primary', payload='{"command":"help"}')
    kb.add_line()
    kb.add_button(ans.conf, color='primary', payload='{"command":"conf"}')
    vk.send_keyboard(user, kb.get_keyboard(), msg, attach=attach)


def auth_button(user, msg=ans.help, links=False):
    kb = vk.VkKeyboard(inline=True)

    if not check_auth(user.user_id):
        kb.add_button(ans.not_auth, color='negative', payload='{"command":"auth_false"}')
        if ans.help == msg:
            msg += ans.val_addition
        if links:
            kb.add_line()

    if links:
        kb.add_openlink_button('Твой ФФ!', link='https://app.profcomff.com')
        kb.add_openlink_button('Telegram-бот', link='https://t.me/profcomff_print_bot')

    if len(kb.lines[0]) == 0:
        vk.write_msg(user, msg)
    else:
        vk.send_keyboard(user, kb.get_keyboard(), msg)


def keyboard_browser(user, str_payload):
    match json.loads(str_payload)['command']:
        case 'start':
            main_page(user)
            auth_button(user, links=True)
        case 'help':
            main_page(user)
            auth_button(user, links=True)
        case 'conf':
            main_page(user, ans.conf_full)
        case 'auth_false':
            if check_auth(user.user_id):  # Prevent to tap on old button
                vk.write_msg(user, ans.val_already)
                return
            vk.write_msg(user, ans.val_need)
            vk.write_msg(user, ans.exp_name)
        case _:
            main_page(user)
            vk.write_msg(user, 'Похоже бот обновился.\nВыполните команду /start')