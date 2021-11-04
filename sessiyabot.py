# print-bot
# for proffcom_ff
# Marakulin Andrey @annndruha
# 2021
from threading import Thread
import time

from core import chat_module

if __name__ == '__main__':

    chat_thread = Thread(target=chat_module.chat_loop)
    chat_thread.start()

    time.sleep(1)
    print("=============== BOT START ===============")

    chat_thread.join()