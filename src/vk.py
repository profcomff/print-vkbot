# Marakulin Andrey @annndruha
# 2023
import logging

import requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotEvent, VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id
from vk_api.vk_api import DEFAULT_USERAGENT

from src.settings import settings


class VkSession(requests.Session):
    def request(self, *args, **kwargs):
        kwargs.setdefault('timeout', (5, 15))
        return super().request(*args, **kwargs)


session = VkSession()
session.headers['User-Agent'] = DEFAULT_USERAGENT
vk = VkApi(token=settings.BOT_TOKEN, api_version=settings.API_VERSION, session=session)


def create_longpoll():
    return VkBotLongPoll(vk, group_id=settings.GROUP_ID)


class EventUser:
    def __init__(self, event: VkBotEvent):
        if event.type == VkBotEventType.MESSAGE_ALLOW:
            self.user_id = event.obj['user_id']
            self.message = ''
            self.attachments = []
        else:
            self.user_id = event.message['from_id']
            self.message = event.message['text']
            self.attachments = event.message.attachments

        logging.info('VK event %s from user %s', event.type, self.user_id)


def send(user: EventUser, message: str, keyboard: VkKeyboard | None = None):
    if user is None:
        return
    values = {'user_id': user.user_id, 'message': message, 'dont_parse_links': 1, 'random_id': get_random_id()}
    if keyboard is not None:
        values['keyboard'] = keyboard

    vk.method('messages.send', values)
