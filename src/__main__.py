import asyncio
import logging

from src.handlers import event_loop
from src.settings import get_settings, sync_from_server

logging.getLogger("httpx").setLevel(logging.WARNING)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


if __name__ == "__main__":
    asyncio.run(sync_from_server())
    settings = get_settings()
    logging.info("=== BOT START ===")
    while True:
        event_loop()
