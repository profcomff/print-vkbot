# Marakulin Andrey @annndruha
# 2021
import logging
import time
import traceback

import core.answers as ru
import func.vkontakte_functions as vk
import core.keybords as kb


def order_print():
    pass


def validate_proff():
    pass


def check_proff():
    pass


def message_analyzer(user):
    try:
        if len(user.message) <= 0 and len(user.attachments) == 0:
            kb.main_page(user.user_id, ru.kb_ans['help'])
        elif len(user.message) > 0 and len(user.attachments) == 0:
            # TODO: Validate number and remember or help
            vk.write_msg(user.user_id, "Validate number and remember or help")
        elif len(user.message) <= 0 and len(user.attachments) > 0:
            # TODO: Check number in base and print
            vk.write_msg(user.user_id, "Check number in base and print")
        elif len(user.message) > 0 and len(user.attachments) > 0:
            # TODO:Validate number and remember and print
            vk.write_msg(user.user_id, "TODO:Validate number and remember and print")


        # valid = user.message.isnumeric()
        # if not valid:
        #     kb.main_page(user.user_id, ru.kb_ans['help'])
        #     return
        # else:
        #     vk.write_msg(user.user_id, ans, attach)
        #
        # attach = None
        # open_kb = True
        #
        # ans = "Главное меню"
        # if open_kb:
        #     kb.main_page(user.user_id, ans)
        # else:
        #     vk.write_msg(user.user_id, ans, attach)

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
