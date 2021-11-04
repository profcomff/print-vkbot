# print-bot
# for proffcom_ff
# Marakulin Andrey @annndruha
# 2021
from threading import Thread
import time
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

from core import chat

if __name__ == '__main__':

    chat_thread = Thread(target=chat.chat_loop)
    chat_thread.start()

    time.sleep(1)
    logging.info("=============== BOT START ===============")

    chat_thread.join()