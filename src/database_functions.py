# Marakulin Andrey @annndruha
# 2021
import psycopg2

from src.settings import Settings


settings = Settings()

connection = psycopg2.connect(settings.DB_DSN)


def reconnect():
    global connection
    connection = psycopg2.connect(settings.DB_DSN)


def check_and_reconnect():
    try:
        cur = connection.cursor()
        cur.execute('SELECT 1')
    except psycopg2.OperationalError:
        reconnect()


def get_user(user_id):
    with connection.cursor() as cur:
        cur.execute('SELECT * FROM bot_vk_print.vk_user WHERE vk_id=%s;', (user_id,))
        return cur.fetchone()


def add_user(user_id, surname, number):
    with connection.cursor() as cur:
        cur.execute(
            'INSERT INTO bot_vk_print.vk_user (vk_id,surname,number) VALUES (%s,%s,%s);', (user_id, surname, number)
        )
        connection.commit()


def update_user(user_id, surname, number):
    with connection.cursor() as cur:
        cur.execute('UPDATE bot_vk_print.vk_user SET surname=%s,number=%s WHERE vk_id=%s;', (surname, number, user_id))
        connection.commit()
