import os

# __all__ = ['TOKEN', 'FILE_DIR', 'USERS_PATH', 'PROJECT_NAME', 'MSG_NO_GROUP']

TOKEN = '5751721909:AAFYdHoeMBPAXVc_vi0NeTsNZ4nvrXa6rq8'
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_PATH = os.path.join(FILE_DIR, 'users.json')
PROJECT_NAME = 'telegram-schedule-bot'

MSG_NO_GROUP = 'Введите команду /group <название группы> для установки группы по умолчанию.'
MSG_NO_LESSONS_TODAY = 'Сегодня пар нет'
MSG_NO_LESSONS_TOMORROW = 'Завтра пар нет'
MSG_UNKNOWN_COMMAND = 'Неизвестная команда'