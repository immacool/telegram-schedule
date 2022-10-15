import json
import os
from collections import defaultdict
from schedule_parser import get_schedule
from loguru import logger

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from globals import *
from utils import format_lesson

# Настройка логирования
# Отключение логгирования в консоль
logger.remove()
logger.add(f'{PROJECT_NAME}.log',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1 week',
           compression='zip')

logger.info('Загрузка пользователей...')


def load_users() -> dict:
    ''' Загружает пользователей из файла '''
    if os.path.exists(USERS_PATH):
        logger.success('Файл с пользователями найден.')
        with open(USERS_PATH, 'r', encoding='utf8') as file:
            users = json.load(file)
    else:
        logger.warning('Файл с пользователями не найден.')
        users = defaultdict(dict)
    return users


async def save_users() -> None:
    ''' Сохраняет пользователей в файл '''
    with open(USERS_PATH, 'w', encoding='utf8') as file:
        json.dump(users, file, ensure_ascii=False, indent=4)
    logger.success('Файл пользователей изменен.')


# Загрузка пользователей
users = load_users()


def authed(need_group=True):
    ''' Декоратор для проверки авторизации пользователя и его группы '''
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            
            if str(chat_id) not in users:
                users[str(chat_id)] = {}
                await save_users()
                await update.message.reply_text(MSG_NO_GROUP)
                return
            
            if need_group and not users[str(chat_id)].get('group'):
                await update.message.reply_text(MSG_NO_GROUP)
                return
            
            await func(update, context)
        return wrapper
    return decorator


@authed()
async def start_command(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    ''' Отправляет кнопки с действиями
        - Пары на сегодня - присылает расписание на сегодня
        - Следующая пара - присылает следующую пару
        - Пары на завтра - присылает расписание на завтра
        - Переключить оповещания - переключает автооповещения в виде рассылки '''
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Пары на сегодня', callback_data='today')],
        [InlineKeyboardButton('Следующая пара', callback_data='next')],
        [InlineKeyboardButton('Пары на завтра', callback_data='tomorrow')],
        [
            InlineKeyboardButton('Переключить оповещания',
                                    callback_data='toggle')
        ],
    ])
    await update.message.reply_text('Выберите действие:',
                                    reply_markup=reply_markup)


@authed()
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    group = users[str(chat_id)]['group']

    schedule = get_schedule(group)
    today_lessons = schedule.today_lessons()
    
    if not today_lessons:
        await query.edit_message_text(MSG_NO_LESSONS_TODAY)
        return
    
    await query.edit_message_text(f'Пары на сегодня [{today_lessons[0].date}]')
    for lesson in today_lessons:
        message = format_lesson(lesson)
        await query.message.reply_text(message)


@authed()
async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    group = users[str(chat_id)]['group']

    schedule = get_schedule(group)
    next_lesson = schedule.next_lesson()
    
    if not next_lesson:
        await query.edit_message_text(MSG_NO_LESSONS_TODAY)
        return
        
    await query.edit_message_text(f'Следующая пара')
    message = format_lesson(next_lesson)
    await query.message.reply_text(message)
        


@authed()
async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    group = users[str(chat_id)]['group']

    schedule = get_schedule(group)
    tomorrow_lessons = schedule.tomorrow_lessons()
    
    if not tomorrow_lessons:
        await query.edit_message_text(MSG_NO_LESSONS_TOMORROW)
        return
        
    await query.edit_message_text(
        f'Пары на завтра [{tomorrow_lessons.date}]')
    for lesson in tomorrow_lessons:
        await query.message.reply_text(format_lesson(lesson))



@authed()   
async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''' Переключает автооповещения в виде рассылки пар на
         день и следующую пару '''
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    user = users[str(chat_id)]
    user['notify'] = not user['notify']
    await save_users()
    await query.edit_message_text(
        'Автооповещения включены' if user['notify'] else
        'Автооповещения выключены')


@authed(need_group=False)
async def group_command(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('Введите название группы.')
        return

    global users
    chat_id = update.effective_chat.id
    group = context.args[0]
    users[str(chat_id)]['group'] = group
    with open(USERS_PATH, 'w', encoding='utf8') as file:
        json.dump(users, file, ensure_ascii=False)
    await update.message.reply_text(f'Группа {group} установлена по умолчанию.'
                                    )
    await start_command(update, context)


async def unknown_command(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(MSG_UNKNOWN_COMMAND)


async def error_handler(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f'Update {update} caused error {context.error}')


def main() -> None:
    application = (Application.builder().token(TOKEN).build())

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("group", group_command))

    application.add_handler(CallbackQueryHandler(today, pattern='today'))
    application.add_handler(CallbackQueryHandler(next, pattern='next'))
    application.add_handler(CallbackQueryHandler(tomorrow, pattern='tomorrow'))
    application.add_handler(CallbackQueryHandler(toggle, pattern='toggle'))

    unknown_handler = MessageHandler(filters.COMMAND, unknown_command)
    application.add_handler(unknown_handler)
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
