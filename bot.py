import asyncio
from aiogram import Dispatcher
from config import bot, db
from aiogram.fsm.storage.memory import MemoryStorage

from hendlers.admin_hendlers import admin_router
from hendlers.user_henlders import user_router  

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(admin_router)
dp.include_router(user_router)

async def main():
    await db.connect()
    await db.create_tables()
    await dp.start_polling(bot)
    await db.close()

if __name__ == '__main__':
    asyncio.run(main())
