# Marakulin Andrey @annndruha
# 2023

import requests

import src.vk as vk
from src.db import Session, VkUser
from src.settings import settings


def check_union_member(user: vk.EventUser, surname, number) -> None | tuple:
    if not surname or not number:
        return None
    r = requests.get(
        url=settings.PRINT_URL + '/is_union_member', params=dict(surname=surname, number=number, v=1), timeout=(5, 10)
    )
    r.raise_for_status()
    if r.json() is True:
        return user.user_id, surname, number
    return None


def check_user_in_db(user: vk.EventUser) -> None | tuple:
    with Session() as session:
        data: VkUser | None = session.query(VkUser).filter(VkUser.vk_id == user.user_id).one_or_none()
    if data is not None:
        return user.user_id, data.surname, data.number
    return None


def check(user: vk.EventUser) -> None | tuple:
    """
    :param user: Object of vk.EventUser
    :return: db_requisites tuple or None if user not authenticated
    """
    credentials = check_user_in_db(user)
    if credentials is None:
        return None
    _, surname, number = credentials
    return check_union_member(user, surname, number)


def add_user(user: vk.EventUser, surname, number) -> None:
    with Session() as session:
        session.add(VkUser(vk_id=user.user_id, surname=surname, number=number))
        session.commit()


def update_user(user: vk.EventUser, surname, number) -> None:
    with Session() as session:
        data: VkUser | None = session.query(VkUser).filter(VkUser.vk_id == user.user_id).one_or_none()
        data.surname = surname
        data.number = number
        session.commit()
