# Marakulin Andrey @annndruha
# 2021
import time
import traceback
import datetime

import data.ru_dictionary as ru
import func.vkontakte_functions as vk
import core.keybords as kb


def timestamp():
    return "[" + str(datetime.datetime.strftime(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))),
                                                '%d.%m.%Y %H:%M:%S')) + "]"


def message_analyzer(user):
    try:
        if len(user.message) <= 0:
            kb.main_page(user.user_id, ru.kb_ans['help'])

        valid = user.message.isnumeric()
        if not valid:
            kb.main_page(user.user_id, ru.kb_ans['help'])
            return
        else:
            vk.write_msg(user.user_id, ans, attach)

        attach = None
        open_kb = True

        ans = "Главное меню"
        if open_kb:
            kb.main_page(user.user_id, ans)
        else:
            vk.write_msg(user.user_id, ans, attach)

    except OSError as err:
        raise err
    except BaseException as err:
        ans = dict.errors['im_broken']
        vk.write_msg(user.user_id, ans)
        print(f"---{timestamp()} Unknown Exception (message_analyzer), description:")
        traceback.print_tb(err.__traceback__)
        print(str(err.args))


def chat_loop():
    while True:
        # print(f"==={timestamp()} CHAT MODULE RESTART")
        try:
            vk.reconnect()
            for event in vk.longpoll.listen():
                if event.type == vk.VkEventType.MESSAGE_NEW and event.to_me:
                    vk_user = vk.user_get(event.user_id)
                    user = vk.User(event.user_id, event.text, (vk_user[0])['first_name'], (vk_user[0])['last_name'])

                    try:
                        kb.keyboard_browser(user, event.payload)
                    except AttributeError:
                        message_analyzer(user)

        except OSError as err:
            print(f"---{timestamp()} OSError (longpull_loop), description:")
            traceback.print_tb(err.__traceback__)
            print(err.args)
            try:
                print(f"---{timestamp()} Try to recconnect VK...")
                vk.reconnect()
                print(f"---{timestamp()} VK connected successful")
                time.sleep(1)
            except:
                print(f"---{timestamp()} Recconnect VK failed")
                time.sleep(10)

        except BaseException as err:
            print(f"---{timestamp()} BaseException (longpull_loop), description:")
            traceback.print_tb(err.__traceback__)
            print(err.args)
            time.sleep(5)

        except:
            print('---Something go wrong. (chat_loop)')
