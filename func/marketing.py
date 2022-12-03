import json
import requests
import configparser
from urllib.parse import urljoin


config = configparser.ConfigParser()
config.read('auth.ini')
MARKETING_URL = config["marketing_url"]
PRINT_URL = config["print_url"]


def register(**user_info):
    requests.post(
        urljoin(MARKETING_URL, "v1/action"),
        json={
            'user_id': -2,
            'action': 'print bot register',
            'additional_data': json.dumps(user_info),
            'path_from': 'https://vk.com/im',
        }
    )


def register_exc_wrong(**user_info):
    requests.post(
        urljoin(MARKETING_URL, "v1/action"),
        json={
            'user_id': -2,
            'action': 'print bot register exc wrong creds',
            'additional_data': json.dumps(user_info),
            'path_from': 'https://vk.com/im',
        }
    )


def print(**print_info):
    requests.post(
        urljoin(MARKETING_URL, "v1/action"),
        json={
            'user_id': -2,
            'action': 'print bot register',
            'additional_data': json.dumps(print_info),
            'path_from': 'https://vk.com/im',
            'path_to': urljoin(PRINT_URL, f'/file/{print_info.get("pin")}'),
        }
    )


def print_exc_many(**print_info):
    requests.post(
        urljoin(MARKETING_URL, "v1/action"),
        json={
            'user_id': -2,
            'action': 'print bot exc many',
            'additional_data': json.dumps(print_info),
            'path_from': 'https://vk.com/im',
        }
    )


def print_exc_format(**print_info):
    requests.post(
        urljoin(MARKETING_URL, "v1/action"),
        json={
            'user_id': -2,
            'action': 'print bot exc format',
            'additional_data': json.dumps(print_info),
            'path_from': 'https://vk.com/im',
        }
    )


def print_exc_other(**print_info):
    requests.post(
        urljoin(MARKETING_URL, "v1/action"),
        json={
            'user_id': -2,
            'action': 'print bot exc format',
            'additional_data': json.dumps(print_info),
            'path_from': 'https://vk.com/im',
        }
    )
