import bs4
import requests

from schedule import Schedule, Lesson


def get_schedule(group) -> Schedule:
    url = 'https://rksi.ru/schedule'
    config = {
        'data': {
            'group': group.encode('windows-1251'),
            'stt': 'Показать!'.encode('windows-1251')
        },
        'headers': {
            'accept-enconding': 'gzip, deflate, br',
            'content-type': 'application/x-www-form-urlencoded',
            'connection': 'keep-alive',
        }
    }
    response = requests.post(url, data=config['data'], timeout=5)
    response.encoding = 'windows-1251'
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    schedule_raw = soup.find_all('form')[-1].find_next_siblings()
    schedule_raw = ''.join([str(tag)
                            for tag in schedule_raw[1:]]).split('<hr/>')[:-1]
    sched = Schedule()
    for day in schedule_raw:
        for tag in ['<b>', '</b>', '<br/>', '<p>', '</p>']:
            day = day.replace(tag, '#')
        day = [i for i in day.split('#') if i]
        date = day[0]

        idx = 1
        while idx < len(day) - 1:
            skip_idx = 3
            time = day[idx]
            subject = day[idx + 1]

            if idx + 2 < len(day) and ',' in day[idx + 2]:
                tmp = day[idx + 2].split(',')
                if len(tmp) == 2:
                    teacher, room = tmp
                elif len(tmp) == 1:
                    teacher, room = tmp[0] if tmp[0] else '-', tmp[1] if tmp[
                        1] else '-'
            else:
                teacher, room = '-', '-'
                skip_idx = 2

            sched.add_lesson(Lesson(subject, teacher, room.strip(), time, date))
            idx += skip_idx

    return sched


if __name__ == '__main__':
    # from utils import format_lesson
    
    schedule = get_schedule('ПОКС-44b')
    print(schedule.week_schedule())
