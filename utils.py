import datetime


def format_lesson(lesson: 'Lesson') -> str:
    message = f'🕐 {lesson.time}\n' \
              f'📃 {lesson.name}\n' \
              f'🧑‍🏫 {lesson.teacher}  | 🚪 {lesson.room}'
    return message


def str_to_date(date: str) -> datetime.date:
    ''' Конвертирует строку вида "10 октября, четверг" в datetime.date '''
    months = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }
    day = int(date[:2])
    month = months[date[3:].split(',')[0].strip()]
    return datetime.date(datetime.date.today().year, month, day)
