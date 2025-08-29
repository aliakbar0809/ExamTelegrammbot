from aiogram import Bot
from database.db import DatabaseConfig

bot = Bot('8346787975:AAG8UzjEiON8kUScas2vURRYbpg1qb39wMk')

# GROUP_ID = -4862153229


db = DatabaseConfig(
    user='postgres',
    password='softclub1122',
    db_name='Salon_bot'
)


