# Marakulin Andrey @annndruha
# 2021

kb_ans = {
    'next': 'Далее ->',
    'back': '<- Назад',
    'cancel': 'Отменить',
    'start': 'Начать',
    'main_menu': 'Главное меню',
    'help': 'Чат-бот бесплатного принтера.\n'
            'Прикрепите файл к сообщению и он сразу же отправится на печать! '
            'Поддерживаются только pdf файлы размером не больше 3МБ. '
            'В одном сообщении только один файл.'
}

help_ans = {
    'помогите': kb_ans['help'],
    'помощь': kb_ans['help'],
    'help': kb_ans['help'],
    'как ': kb_ans['help'],
    'инструкция': kb_ans['help'],
    'начать': kb_ans['help'],
    'старт': kb_ans['help'],
    'start': kb_ans['help']
}

errors = {
    'not_available': 'К сожалению, действие временно недоступно',
    'im_broken': 'Глубоко внутри меня что-то сломалось...',
    'kb_error': 'Ошибка клавиатуры, попробуйте текстом',
}

greetings = {
    'night': 'Доброй ночи',
    'morning': 'Доброе утро',
    'day': 'Добрый день',
    'evening': 'Добрый вечер'
}


def numerals_days(n):
    n = n % 100
    if (10 < n) and (n < 20):
        return ' дней'
    else:
        n = n % 10
        if (n == 0) or (n >= 5):
            return ' дней'
        elif n == 1:
            return ' день'
        elif (n > 1) and (n < 5):
            return ' дня'
