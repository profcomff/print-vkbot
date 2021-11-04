# Marakulin Andrey @annndruha
# 2021
import logging
import time
import traceback
import requests

import core.answers as ru
import func.vkontakte_functions as vk
import core.keybords as kb


def get_attachments(user):
    pass


def order_print(user):
    vk.write_msg(user.user_id, "Try to order print")
    r = requests.post('https://app.profcomff.com/print', data={'surname': 'value',
                                                               'number': user.last_name,
                                                               'filename': 'test'})
    logging.info(r)


# TODO: Validate number and remember or help
def validate_proff(user):
    vk.write_msg(user.user_id, "Try to validate number and save it to base")


# TODO: Check number in base and print
def check_proff(user):
    vk.write_msg(user.user_id, "Check number in base")


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


def chat_loop():
    while True:
        try:
            vk.reconnect()
            for event in vk.longpoll.listen():
                if vk.ismessage_new_to_me(event):
                    vk_user = vk.user_get(event.user_id)
                    user = vk.User(event.user_id, event.text,
                                   event.attachments, (vk_user[0])['first_name'], (vk_user[0])['last_name'])

                    try:
                        kb.keyboard_browser(user, event.payload)
                    except AttributeError:
                        message_analyzer(user)

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
