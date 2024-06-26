# Marakulin Andrey @annndruha
# 2023

from dataclasses import dataclass


@dataclass
class Answers:
    hey: str = 'Привет!'
    not_auth = 'Не авторизовано'
    inst = 'Инструкция'
    conf = 'Конфиденциальность'

    conf_full = (
        '❗️ Файлы, которые вы отправляете через бота, будут храниться в течение нескольких месяцев '
        'на сервере в Москве, а также в этом чате ВКонтакте.'
        '\nДоступ к файлам имеет узкий круг лиц, ответственных за работоспособность сервиса печати.'
        '\nМы НЕ рекомендуем использовать данный сервис для печати конфиденциальных документов!'
    )

    ask_help = ['привет', 'помогите', 'помощь', 'help', 'как ', 'инструкция', 'начать', 'Начать', 'старт', 'start']
    help = (
        'Я вк-бот бесплатного принтера профкома студентов физического факультета МГУ!\n\n'
        '❔ Отправьте PDF файл и получите PIN для печати. Поддерживаются только .PDF файлы размером не более 3МБ.'
        '\nС этим PIN необходимо подойти к принтеру и ввести его в терминал печати. '
        'Либо отсканировать QR-код на принтере с помощью ссылки. После этого начнётся печать.'
        '\n\n💻 Бот разработан группой программистов профкома, как и приложение Твой ФФ!'
        '\nВ приложении вы сможете найти больше настроек печати, расписание и много других возможностей.'
        '\nТак же есть Telegram-бот для печати.'
    )

    err_bd = '❌ Ошибка базы данных. Попробуйте позже.'
    err_print = '❌ Ошибка сервера печати. Попробуйте позже.'
    err_payload = '🐩 Похоже бот обновился.\nВыполните команду /start'
    err_vk = '🐩 Ошибка взаимодействия с ВКонтакте. Попробуйте позже.'
    err_kb = '🐩 Ошибка клавиатуры, что-то пошло не так'
    err_fatal = '🐩 Глубоко внутри меня что-то сломалось...'

    val_pass = '✅ Поздравляю! Проверка пройдена и данные сохранены для этого аккаунта ВК. Можете присылать pdf.'
    val_name = 'Иванов\n1234567'
    val_update_pass = '✅ Поздравляю! Проверка пройдена и данные обновлены.'
    val_already = 'Вы уже успешно авторизованы. Можете присылать файл на печать.'
    val_addition = '\n\nНо для начала нужно авторизоваться. Нажмите на кнопку ниже:'
    val_need = (
        '⚠ Для использования принтера необходимо авторизоваться.'
        '\nВведите фамилию и номер профсоюзного билета в формате:'
    )
    val_fail = (
        '❌ Проверка не пройдена. Удостоверьтесь что вы состоите в профсоюзе и правильно ввели данные.'
        '\n\nВведите фамилию и номер профсоюзного билета в формате:'
    )
    val_fail_format = (
        'Я вас не понимаю. Если вы хотите обновить данные авторизации введите фамилию и '
        'номер профсоюзного билета в формате:'
    )
    val_unknown_message = (
        'Сообщение не распознано. Если вы хотите обновить данные авторизации введите фамилию и '
        'номер профсоюзного билета в формате:'
    )

    warn_filesize = '⚠️ Файл слишком большой. Мы принимаем файлы размером ДО 3 МБ'
    warn_many_files = '⚠️ Файлов слишком много. Прикрепите только один файл pdf.'
    warn_unreadable_file = '⚠️ Я не смог прочитать файл. Проверьте его целостность и формат, я работаю только с pdf.'
    warn_only_pdfs = '⚠️ Я умею печатать только документы в формате pdf.'

    send_to_print = '✅ Файл "{}" успешно загружен. Для печати подойдите к принтеру и введите PIN: \n\n{}'
    qr_button_text = '📷 Печать по QR'


ans = Answers()
