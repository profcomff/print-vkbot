# sessiyabot/func/vk_functions
# - vk functions
# Marakulin Andrey @annndruha
# 2019
import time
import datetime
import json
import traceback
import requests
import configparser

from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard

config = configparser.ConfigParser()
config.read('auth.ini')

GROUP_ID = config['auth_vk']['group_id']
GROUP_TOKEN = config['auth_vk']['group_token']
API_VERSION = "5.120"

vk = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)  # Auth with community token
longpoll = VkBotLongPoll(vk, group_id=GROUP_ID)  # Create a longpull variable


class User:
    def __init__(self, user_id, message, attachments, first_name, last_name):
        self.user_id = user_id
        self.message = message
        self.first_name = first_name
        self.last_name = last_name
        self.attachments = attachments


def reconnect():
    global vk
    global longpoll
    vk = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
    longpoll = VkBotLongPoll(vk, group_id=GROUP_ID)


def user_get(user_id):
    return vk.method('users.get', {'user_ids': user_id})


def write_msg(user_id, message=None, attach=None, parse_links=False):
    params = {'user_id': user_id, 'random_id': get_random_id()}

    if message is not None and attach is not None:
        params['message'] = message
        params['attachment'] = attach
    elif message is not None and attach is None:
        params['message'] = message
    elif message is None and attach is not None:
        params['attachment'] = attach
    if not parse_links:
        params['dont_parse_links'] = 1

    vk.method('messages.send', params)


def send_keyboard(user_id, kb, message, attach=None):
    if attach is None:
        vk.method('messages.send',
                  {'user_id': user_id, 'keyboard': kb, 'message': message, 'random_id': get_random_id()})
    else:
        vk.method('messages.send', {'user_id': user_id, 'keyboard': kb, 'message': message, 'attachment': attach,
                                    'random_id': get_random_id()})


# def get_attach_str(user_id):
#     getMessagesUploadServer = vk.method('photos.getMessagesUploadServer', {'peer_id': user_id})
#     upload_url = getMessagesUploadServer['upload_url']
#
#     file = {'photo': open('data/temp.png', 'rb')}
#
#     ur = requests.post(upload_url, files=file).json()
#
#     photo = vk.method('photos.saveMessagesPhoto', {'photo': ur['photo'], 'server': ur['server'], 'hash': ur['hash']})
#
#     type = 'photo'
#     media_id = str(photo[0]['id'])
#     owner_id = str(photo[0]['owner_id'])
#     access_key = photo[0]['access_key']
#     at = type + owner_id + '_' + media_id + '_' + access_key
#     return at
#
#
# def get_doc_info(docid):
#     return vk.method('docs.getById', {'docs': docid + ',' + docid})
