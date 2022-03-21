# Print-bot

## Бот для отправки файлов на печать на принтер
Печать через сайт: https://www.profcomff.com/work/obshkom/print

Этот бот вк: https://vk.com/profcomff_print

## Ключевые особенности

* Возможность отправлять файлы pdf на сервер печати
* Возможность проверки пользователя
* Валидация принимаемых типов сообщений
* Красивые клавиатуры

## Запуск вне докера

* Переименуйте `auth_example.ini` в `auth.ini`
* Заполните все поля в соответствии с своими токенами, базой данных и сервером печати.
* Создайте виртуальное окружение `create_venv.bat` или `pip install -r requirements.txt`
* Запуск: `python print-bot.py`

## Запуск в докере

Запуск контейнера

```bash
docker run -d --name print-bot --restart always -v /root/print-bot:/print-bot imageid
```

Положите `auth.ini` в `/root/print-bot` и перезапустите контейнер:

```bash
docker stop print-bot
docker start print-bot
```
