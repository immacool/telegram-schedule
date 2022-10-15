import datetime
from collections import defaultdict
from typing import List

from utils import format_lesson, str_to_date


class Lesson:
    duration = 90

    def __init__(self, name, teacher, room, time, date):
        self.name = name
        self.teacher = teacher
        self.room = room
        self.time = time
        self.date = str_to_date(date)

        self.start_time = datetime.datetime.strptime(time.split()[0], '%H:%M')
        self.start_time = self.start_time.replace(
            year=datetime.datetime.now().year,
            month=self.date.month,
            day=self.date.day)
        self.end_time = self.start_time + datetime.timedelta(
            minutes=self.duration)

    def time_to_end(self) -> int:
        ''' Возвращает время до конца пары в минутах '''
        return (self.start_time + datetime.timedelta(minutes=self.duration) -
                datetime.datetime.now()).seconds // 60

    def time_to_end_str(self) -> str:
        ''' Возвращает время до конца пары в формате N дней, N часов, N минут '''
        hours, minutes = divmod(self.time_to_end(), 60)
        days = hours // 24
        hours %= 24
        string = ''
        string += f'{days} дней ' if days else ''
        string += f'{hours} часов ' if hours else ''
        string += f'{minutes} минут' if minutes else ''
        return string

    def __str__(self) -> str:
        return f'{self.name} ({self.teacher}, {self.room})'


class Schedule:

    def __init__(self) -> None:
        self.lessons = defaultdict(list)

    def current_lesson(self) -> Lesson or None:
        ''' Возвращает текущую пару '''
        for lesson in self.today_lessons():
            if datetime.datetime.now() < lesson.end_time:
                return lesson

    def add_lesson(self, lesson: Lesson) -> None:
        ''' Добавляет пару в расписание по ключу даты '''
        if lesson not in self.lessons[lesson.date]:
            self.lessons[lesson.date].append(lesson)

    def today_lessons(self) -> List[Lesson]:
        ''' Возвращает список пар на сегодня '''
        today = datetime.date.today()
        return self.lessons.get(today, [])

    def tomorrow_lessons(self) -> List[Lesson]:
        ''' Возвращает список пар на завтра '''
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        return self.lessons.get(tomorrow, [])

    def week_schedule(self) -> List[List[Lesson]]:
        ''' Возвращает расписание на следующие 7 дней '''
        now = datetime.datetime.now()
        week = now + datetime.timedelta(days=7)
        schedule = []
        while now < week:
            schedule += f'{now.strftime("%d.%m.%Y")}:\n'
            schedule += self.lessons.get(now.date(), [])
            now += datetime.timedelta(days=1)
        return schedule

    def next_lesson(self) -> Lesson:
        ''' Возвращает следующую пару '''
        for lesson in self.today_lessons():
            if datetime.datetime.now() < lesson.start_time:
                return lesson

    def __str__(self) -> str:
        return '\n'.join([
            f'==== {date} ====\n' +
            '\n'.join([str(lesson) for lesson in lessons])
            for date, lessons in self.lessons.items()
        ])
