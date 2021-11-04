# sessiyabot/func/datetime_functions
# -conversions and validators date and time types
# Marakulin Andrey @annndruha
# 2019
import datetime


# Now objects
def datetime_now_obj():
    delta = datetime.timedelta(hours=3)  # MoscowUTC
    tzone = datetime.timezone(delta)
    return datetime.datetime.now(tzone)


def date_now_obj():
    return datetime_now_obj().date()


def time_now_obj():
    return datetime.time(datetime_now_obj().hour, datetime_now_obj().minute)  # Drop seconds


# Obj to string format
def datetime_to_str(datetime_object):
    return datetime.datetime.strftime(datetime_object, '%d.%m.%Y %H:%M')


def date_to_str(date_obj):
    return datetime.date.strftime(date_obj, '%d.%m.%Y')


def time_to_str(time_obj):
    return datetime.time.strftime(time_obj, '%H:%M')


# From string to obj
def str_to_date(string):
    template = ['%d.%m.%Y', '%Y.%m.%d', '%Y-%m-%d', '%d.%m.%y', '%y.%m.%d', '%d,%m,%Y', '%Y,%m,%d', '%d,%m,%y',
                '%y,%m,%d']
    for t in template:
        try:
            d = datetime.datetime.strptime(string, t).date()
        except:
            return_None = 0
        else:
            return datetime.datetime.strptime(string, t).date()


def str_to_time(string):
    template = ['%H:%M', '%H.%M', '%H,%M']
    for t in template:
        try:
            d = datetime.datetime.strptime(string, t).time()
        except:
            return_None = 0
        else:
            return datetime.datetime.strptime(string, t).time()


def str_to_datetime(string):
    try:
        s = string.split(' ')
        date = str_to_date(s[0])
        time = str_to_time(s[1])
        datetime = datetime.datetime.combine(date, time)
        return datetime
    except:
        return_None = 0


# Validate format functions
def validate_date(date_text):
    try:
        if isinstance(date_text, datetime.date):
            return True
        else:
            if str_to_date(date_text) != None:
                return True
            else:
                return False
    except:
        return False


def validate_time(time_text):
    try:
        if isinstance(time_text, datetime.time):
            return True
        else:
            if str_to_time(time_text) != None:
                return True
            else:
                return False
    except:
        return False


def validate_datetime(datetime_text):
    try:
        if isinstance(datetime_text, datetime.datetime):
            return True
        else:
            if str_to_datetime(datetime_text) != None:
                return True
            else:
                return False
    except:
        return False


def validate_tz(tz_text):
    try:
        i = int(tz_text)
        if (i > -16 and i < 10):
            return True
        else:
            return False
    except:
        return False


# Timezone shifters
def shift_time(time, tz):
    try:
        if isinstance(time, str):
            time = str_to_time(time)
        if isinstance(tz, str):
            tz = int(tz)
        date = str_to_date('02.02.2000')
        delta = datetime.timedelta(hours=tz)
        new_time = (datetime.datetime.combine(date, time) + delta).time()
        return new_time
    except:
        return_None = 0


def shift_date(local_date, tz, local_time=None):
    try:
        if isinstance(local_time, str):
            local_time = str_to_time(local_time)
        if isinstance(local_date, str):
            local_date = str_to_date(local_date)
        if isinstance(tz, str):
            tz = int(tz)

        if local_time is None:
            local_time = shift_time(time_now_obj(), tz)

        delta = datetime.timedelta(seconds=3600 * tz)
        local_datetime = datetime.datetime.combine(local_date, local_time)
        new_date = (local_datetime + delta).date()
        return new_date
    except:
        return_None = 0


# Find the nearest date in future by day and month
def neareat_date(day_and_month):
    day = day_and_month.split('.')[0]
    month = day_and_month.split('.')[1]
    y = 0
    stopper = 0
    while stopper < 20:
        str_year = str(date_now_obj().year + y)
        date = day_and_month + '.' + str_year
        if validate_date(date) == True:
            difference = (str_to_date(date) - date_now_obj()).days
            if difference >= 0:
                return 'date ' + date
            else:
                stopper = stopper + 1
                y = y + 1
        else:
            stopper = stopper + 1
            y = y + 1
