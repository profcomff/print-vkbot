# sessiyabot/core/chat_module
# - text anaizer engine, runner and keybord browser
# Marakulin Andrey @annndruha
# 2019
import time
import traceback
import datetime

import psycopg2

from data import ru_dictionary as dict
from func import vkontakte_functions as vk
from func import database_functions as db
from core import engine as eng
from core import keybords as kb
from core import online_monitor as om

def timestamp():
    return "["+str(datetime.datetime.strftime(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours = 3))), '%d.%m.%Y %H:%M:%S'))+"]"

def message_analyzer(user):
    try:
        user.message = (user.message).lower()
        l = len(user.message)

        ans = None
        attach = None
        open_kb = False

        if   (l <= 0):
            ans = dict.errors['null_length']
        elif (l >= 300):
            ans = dict.errors['big_lenght']
        elif ((l == 1) or (l == 2)):
            for keyword in dict.small_message:
                if (user.message == keyword):
                    ans = dict.small_message[keyword]
            if ans is None:
                ans = dict.errors['hm']
        elif ((l > 2) and (l < 300)):
            for keyword in dict.answer:
                if (user.message.find(keyword) >= 0):
                    ans = dict.answer[keyword]
            for keyword in dict.hello:
                if (user.message.find(keyword) >= 0):
                    ans = dict.hello[keyword]
                    open_kb = True
            for keyword in dict.functions:
                if (user.message.find(keyword) >= 0):
                    k = dict.functions[keyword]
                    if k == 0:
                        ans = eng.sessiya_message(user)
                    if k == 1:
                        ans = eng.alter_time(user)
                    if k == 2:
                        ans = eng.alter_date(user)
                    if k == 3:
                        ans = eng.alter_stop(user)
                    if k == 4:
                        ans = eng.alter_tz(user)
                    if k == 5:
                        ans, attach = dict.cheer(user)
                    if k == 6:
                        ans, attach = dict.cheer(user, True)
                    if ((k == 7) or (k==8) or (k==9)):
                        try:
                            if k == 7:
                                ans = om.day_plot(user.user_id)
                            if k==8:
                                ans = om.yesterday_plot(user.user_id)
                            if k==9:
                                ans = om.week_plot(user.user_id)
                        except KeyError:
                            ans = dict.errors['access_denied']
                            attach = None
                        except NameError:
                            ans = dict.errors['young_member']
                            attach = None
                        else:
                            attach = vk.get_attach_str(user.user_id)
            if eng.validate_expression(user.message)==True:
                ans = eng.calculator(user.message)
            if ans == None:
                ans = eng.find_in_internet(user.message)
            if ans == None:
                if user.message.find('?') >= 0:
                    ans = dict.random_answer()
        if ans == None:
            ans = dict.random_not_found()

        if open_kb:
            kb.main_page(user.user_id, ans)
        else:
            vk.write_msg(user.user_id, ans, attach)

    except psycopg2.Error:
        raise err
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
        #print(f"==={timestamp()} CHAT MODULE RESTART")
        try:
            db.reconnect()
            vk.reconnect()
            for event in vk.longpoll.listen():
                if (event.type == vk.VkEventType.MESSAGE_NEW and event.to_me):
                    vk_user = vk.user_get(event.user_id)
                    id = event.user_id
                    first_name = (vk_user[0])['first_name']
                    last_name = (vk_user[0])['last_name']
                    user = vk.User(id, event.text, first_name, last_name)

                    try:
                        kb.keyboard_browser(user, event.payload)
                    except AttributeError:
                        message_analyzer(user)

        except psycopg2.Error as err:
            print(f"---{timestamp()} Database Error (longpull_loop), description:")
            traceback.print_tb(err.__traceback__)
            print(err.args)
            try:
                print(f"---{timestamp()} Try to recconnect database...")
                db.reconnect()
                print(f"---{timestamp()} Database connected successful")
                time.sleep(1)
            except:
                print(f"---{timestamp()} Recconnect database failed")
                time.sleep(10)
            
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