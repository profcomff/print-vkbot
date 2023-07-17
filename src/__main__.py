import logging
from threading import Thread

import src.chat as chat

logging.getLogger("httpx").setLevel(logging.WARNING)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


if __name__ == '__main__':
    chat_thread = Thread(target=chat.chat_loop)
    chat_thread.start()
    logging.info("=== BOT START ===")
    chat_thread.join()
