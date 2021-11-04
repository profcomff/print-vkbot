# Marakulin Andrey @annndruha
# 2021
import json
import logging
import traceback

import func.vkontakte_functions as vk
import core.answers as ru


def main_page(user_id, ans="Главное меню", attach=None):
    kb = vk.VkKeyboard(one_time=False)

    kb.add_button("Начать", color='positive')  # , payload=["next_page", "notify_page"]
    kb.add_line()
    kb.add_button("Инструкция", color='primary', payload=["command", "help"])
    vk.send_keyboard(user_id, kb.get_keyboard(), ans, attach=attach)


def keyboard_browser(user, str_payload):
    try:
        payload = json.loads(str_payload)
        if not isinstance(payload, list):
            main_page(user.user_id)
        elif payload[0] == 'command':
            if payload[1] == 'cancel':
                main_page(user.user_id)
            if payload[1] == 'help':
                ans = ru.kb_ans['help']
                main_page(user.user_id, ans)

        main_page(user.user_id)

    except OSError as err:
        raise err
    except BaseException as err:
        ans = dict.errors['kb_error']
        vk.write_msg(user.user_id, ans)
        logging.error("Unknown Exception (keyboard_browser), description:")
        traceback.print_tb(err.__traceback__)
        logging.error(f"Unknown Exception (keyboard_browser), description: {str(err.args)}")
