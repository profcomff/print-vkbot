# Marakulin Andrey @annndruha
# 2023

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotEvent, VkBotLongPoll
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id

from src.settings import settings


# Auth with community token
vk = VkApi(token=settings.BOT_TOKEN, api_version=settings.API_VERSION)
longpoll = VkBotLongPoll(vk, group_id=settings.GROUP_ID)


def reconnect():
    global vk
    global longpoll
    vk = VkApi(token=settings.BOT_TOKEN, api_version=settings.API_VERSION)
    longpoll = VkBotLongPoll(vk, group_id=settings.GROUP_ID)


class EventUser:
    def __init__(self, event: VkBotEvent):
        self.user_id = event.message['from_id']
        self.message = event.message['text']
        self.attachments = event.message.attachments

        r = vk.method('users.get', {'user_ids': self.user_id})
        self.first_name = r[0]['first_name']
        self.last_name = r[0]['last_name']


def send(user: EventUser, message: str, keyboard: VkKeyboard | None = None):
    if user is None:
        return
    values = {'user_id': user.user_id, 'message': message, 'dont_parse_links': 1, 'random_id': get_random_id()}
    if keyboard is not None:
        values['keyboard'] = keyboard

    vk.method('messages.send', values)
