import logging

from chat import event_loop

logging.getLogger("httpx").setLevel(logging.WARNING)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    logging.info("=== BOT START ===")
    while True:
        event_loop()

