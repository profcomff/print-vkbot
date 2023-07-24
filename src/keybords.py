# Marakulin Andrey @annndruha
# 2023

import json

import src.vk as vk
from src.answers import Answers
from settings import Settings
import src.auth as auth

ans = Answers()
settings = Settings()


def file_settings(pin):
    kb = vk.VkKeyboard(inline=True)
    kb.add_openlink_button(ans.qr_button_text, link=settings.PRINT_URL_QR + str(pin))
    return kb.get_keyboard()


def main_page(user):
    # Send hi message and keyboard
    msg = ans.hey
    kb = vk.VkKeyboard(one_time=False)
    kb.add_button(ans.inst, color='primary', payload='{"command":"help"}')
    kb.add_line()
    kb.add_button(ans.conf, color='primary', payload='{"command":"conf"}')
    vk.send(user, msg, keyboard=kb.get_keyboard())

    # Send help message and inline-keyboard
    msg = ans.help
    kb = vk.VkKeyboard(inline=True)

    # If user not authenticated add button
    if auth.check(user) is None:
        kb.add_button(ans.not_auth, color='negative', payload='{"command":"auth_false"}')
        kb.add_line()
        msg += ans.val_addition

    kb.add_openlink_button('Твой ФФ!', link='https://app.profcomff.com')
    kb.add_openlink_button('Telegram-бот', link='https://t.me/profcomff_print_bot')
    vk.send(user, msg, keyboard=kb.get_keyboard())


def keyboard_browser(user: vk.EventUser, payload: str):
    match json.loads(payload)['command']:
        case 'start':
            main_page(user)
        case 'help':
            main_page(user)
        case 'conf':
            vk.send(user, ans.conf_full)
        case 'auth_false':
            if auth.check(user) is not None:  # Prevent to tap old button
                vk.send(user, ans.val_already)
                return
            vk.send(user, ans.val_need)
            vk.send(user, ans.val_name)
        case _:
            vk.send(user, ans.err_payload)
