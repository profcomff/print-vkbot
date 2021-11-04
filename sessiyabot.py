# sessiyabot
# - Chat bot vk.com for students
# Marakulin Andrey @annndruha
# 2019
from threading import Thread
import time

from core import chat_module
# from func import vkontakte_functions
# from core import notification_module

if __name__=='__main__':
    chat_thread = Thread(target= chat_module.chat_loop)
    chat_thread.start()

    # monitor_thread = Thread(target= vkontakte_functions.followers_monitor)
    # monitor_thread.start()
    #
    # notify_thread = Thread(target= notification_module.notify_loop)
    # notify_thread.start()

    time.sleep(1)
    print("=============== BOT START ===============")

    chat_thread.join()
    # monitor_thread.join()
    # notify_thread.join()