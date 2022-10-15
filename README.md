# Информация

Костыльный телеграм бот для получения расписания занятий с сайта [РКСИ](https://rksi.ru/schedule)

## Зависимости

- Парсер использует [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) и [Requests](https://requests.readthedocs.io/en/master/)
- Бот для телеграм работает на [python-telegram-bot](https://python-telegram-bot.readthedocs.io/en/stable/)
- Python > `3.10.x` для запуска бота и парсера

## Установка

1. Склонировать репозиторий `git clone https://github.com/immacool/telegram-schedule.git`
2. Установить зависимости `pip install -r requirements.txt`
3. Настраиваем бота в файле `config.yaml`
4. Запустить бота `python main.py` (на UNIX подобных системах `python3 main.py`)
