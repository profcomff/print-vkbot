# Marakulin Andrey @annndruha
# 2021
import json
import logging
import traceback
import requests
import psycopg2

import src.answers as ru
import src.vkontakte_functions as vk
import src.database_functions as db


from src.settings import Settings


settings = Settings()


def check_auth(user_id):
    if db.get_user(user_id) is not None:
        _, surname, number = db.get_user(user_id)
        r = requests.get(settings.PRINT_URL+'/is_union_member', params=dict(surname=surname, number=number, v=1))
        if r.json():
            return True
        else:
            return False
    else:
        return False


def main_page(user, ans=ru.kb_ans['hey'], attach=None):
    kb = vk.VkKeyboard(one_time=False)

    kb.add_button(ru.kb_ans['inst'], color='primary', payload='{"command":"help"}')
    kb.add_line()
    kb.add_button(ru.kb_ans['conf'], color='primary', payload='{"command":"conf"}')
    vk.send_keyboard(user, kb.get_keyboard(), ans, attach=attach)


def auth_button(user, ans=ru.kb_ans['help'], links=False):
    kb = vk.VkKeyboard(inline=True)

    if not check_auth(user.user_id):
        kb.add_button(ru.kb_ans['not_auth'], color='negative', payload='{"command":"auth_false"}')
        if ru.kb_ans['help'] == ans:
            ans += ru.val_ans['val_addition']
        if links:
            kb.add_line()

    if links:
        kb.add_openlink_button('Твой ФФ!', link='https://app.profcomff.com')
        kb.add_openlink_button('Telegram-бот', link='https://t.me/profcomff_print_bot')

    if len(kb.lines[0]) == 0:
        vk.write_msg(user, ans)
    else:
        vk.send_keyboard(user, kb.get_keyboard(), ans)


def keyboard_browser(user, str_payload):
    try:
        payload = json.loads(str_payload)  # From str to dict
        if payload['command'] == 'start':
            main_page(user)
            auth_button(user, links=True)
        elif payload['command'] == 'help':
            main_page(user)
            auth_button(user, links=True)
        elif payload['command'] == 'conf':
            main_page(user, ru.kb_ans['conf_full'])
        elif payload['command'] == 'auth_false':
            if check_auth(user.user_id):
                vk.write_msg(user, ru.val_ans['val_already'])
            else:
                vk.write_msg(user, ru.val_ans['val_need'])
                vk.write_msg(user, ru.val_ans['exp_name'])
        else:
            vk.write_msg(user, 'Похоже бот обновился.\nВыполните команду /start')

    except OSError as err:
        raise err
    except psycopg2.Error as err:
        vk.write_msg(user, ru.errors['bd_error'])
        raise err
    except json.decoder.JSONDecodeError as err:
        vk.write_msg(user, ru.errors['print_err'])
        logging.error('JSONDecodeError (message_analyzer), description:')
        traceback.print_tb(err.__traceback__)
        logging.error(err)
    except Exception as err:
        ans = ru.errors['kb_error']
        vk.write_msg(user, ans)
        logging.error(f'Unknown Exception (keyboard_browser), description:')
        logging.error(err)
        traceback.print_tb(err.__traceback__)
