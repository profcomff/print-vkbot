# Marakulin Andrey @annndruha
# 2023

import requests

import src.vk as vk
from src.db import VkUser, session
from src.settings import Settings

settings = Settings()


def check_auth(user: vk.EventUser) -> None | tuple:
    """
    :param user: Object of vk.EventUser
    :return: requisites tuple or None if user not authenticated
    """
    data: VkUser | None = session.query(VkUser).filter(VkUser.vk_id == user.user_id).one_or_none()
    if data is not None:
        r = requests.get(url=settings.PRINT_URL + '/is_union_member',
                         params=dict(surname=data.surname, number=data.number, v=1))
        if r.json():
            return user.user_id, data.surname, data.number
    return None
