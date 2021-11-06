# Marakulin Andrey @annndruha
# 2021

import psycopg2

import configparser
config = configparser.ConfigParser()
config.read('auth.ini')

connection = psycopg2.connect(dbname=config['auth_db']['name'],
                              user=config['auth_db']['user'],
                              password=config['auth_db']['password'],
                              host=config['auth_db']['host'],
                              port=config['auth_db']['port'])


def reconnect():
    global connection
    connection = psycopg2.connect(dbname=config['auth_db']['name'],
                                  user=config['auth_db']['user'],
                                  password=config['auth_db']['password'],
                                  host=config['auth_db']['host'],
                                  port=config['auth_db']['port'])


# Getters
def get_user(user_id):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM printer_bot.vk_users WHERE vk_id=%s;", (user_id,))
        return cur.fetchone()


def add_user(user_id, last_name, proff_number):
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO printer_bot.vk_users (vk_id,last_name,proff_number) VALUES (%s,%s,%s);",
            (user_id, last_name, proff_number))
        connection.commit()



def get_users_who_sub_at(time):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM sessiyabot.users WHERE notifytime=%s AND subscribe=True;", (time,))
        return cur.fetchall()


def get_user_examdate(user_id):
    with connection.cursor() as cur:
        cur.execute("SELECT examdate FROM sessiyabot.users WHERE id=%s;", (user_id,))
        examdate = cur.fetchone()[0]
        return examdate


def get_user_subscribe(user_id):
    with connection.cursor() as cur:
        cur.execute("SELECT subscribe FROM sessiyabot.users WHERE id=%s;", (user_id,))
        subscribe = cur.fetchone()[0]
        return subscribe


# Setters
# Setters with many parametrs:
def add_user_with_time(user_id, new_user_time, sub, first_name, last_name):
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO sessiyabot.users (id,notifytime,subscribe,firstname,lastname) VALUES (%s,%s,%s,%s,%s);",
            (user_id, new_user_time, sub, first_name, last_name))
        connection.commit()


def add_user_with_date(user_id, new_user_date, first_name, last_name):
    with connection.cursor() as cur:
        cur.execute("INSERT INTO sessiyabot.users (id,examdate,firstname,lastname) VALUES (%s,%s,%s,%s);",
                    (user_id, new_user_date, first_name, last_name))
        connection.commit()


def add_user_with_tz(user_id, new_tz, first_name, last_name):
    with connection.cursor() as cur:
        cur.execute("INSERT INTO sessiyabot.users (id,tz,firstname,lastname) VALUES (%s,%s,%s,%s);",
                    (user_id, new_tz, first_name, last_name))
        connection.commit()


def update_user_time_and_sub(user_id, new_user_time, sub):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET notifytime=%s,subscribe=%s WHERE id=%s;",
                    (new_user_time, sub, user_id))
        connection.commit()


# Setters with one parametr:
def set_examdate(user_id, examdate):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET examdate=%s WHERE id=%s;", (examdate, user_id))
        connection.commit()


def set_notifytime(user_id, notifytime):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET notifytime=%s WHERE id=%s;", (notifytime, user_id))
        connection.commit()


def set_subscribe(user_id, subscribe):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET subscribe=%s WHERE id=%s;", (subscribe, user_id))
        connection.commit()


def set_tz(user_id, tz):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET tz=%s WHERE id=%s;", (tz, user_id))
        connection.commit()


def set_firstname(user_id, firstname):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET firstname=%s WHERE id=%s;", (firstname, user_id))
        connection.commit()


def set_lastname(user_id, lastname):
    with connection.cursor() as cur:
        cur.execute("UPDATE sessiyabot.users SET lastname=%s WHERE id=%s;", (lastname, user_id))
        connection.commit()
