from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import db
from database.service import Service
from database.queueEntry import QueueEntry
from keyboards.admin_keyboards import admin_keyboard
from states.admin_states import AdminStates

admin_router = Router()

@admin_router.message(Command("start"))
async def start_admin(message: Message):
    user = await db.pool.fetchrow("SELECT is_staff FROM users WHERE telegram_id=$1", message.from_user.id)
    if user and user["is_staff"]:
        await message.answer("Добро пожаловать, админ!", reply_markup=admin_keyboard)

@admin_router.message(F.text == "➕ Добавить услугу")
async def add_service_text_handler(message: Message, state: FSMContext):
    await message.answer("Введите название, длительность и цену услуги через запятую:\nПример: Стрижка, 30, 1500")
    await state.set_state(AdminStates.waiting_for_service_info)

@admin_router.message(AdminStates.waiting_for_service_info)
async def get_service_info(message: Message, state: FSMContext):
    try:
        name, duration, price = message.text.split(",")
        service = Service(name.strip(), int(duration.strip()), int(price.strip()), db)
        await service.save()
        await message.answer("Услуга добавлена ✅")
    except Exception:
        await message.answer("Ошибка при добавлении услуги ❌")
    await state.clear()

@admin_router.message(F.text == "📋 Посмотреть услуги")
async def view_services_text_handler(message: Message):
    services = await Service("", 0, 0, db).get_all()
    if services:
        msg = "\n".join([f"{s['id']}. {s['name']} – {s['duration']} мин – {s['price']}₽" for s in services])
        await message.answer(f"Список услуг:\n{msg}")
    else:
        await message.answer("Список услуг пуст.")

@admin_router.message(F.text == "📊 Посмотреть очередь")
async def view_queue_text_handler(message: Message):
    entries = await QueueEntry(db=db).get_all()
    if entries:
        msg = "\n".join([f"ID: {e['id']}, Услуга: {e['service']}, Время: {e['scheduled_time']}" for e in entries])
        await message.answer(f"Текущая очередь:\n{msg}")
    else:
        await message.answer("Очередь пуста.")

@admin_router.message(F.text == "👥 Посмотреть пользователей")
async def view_users_text_handler(message: Message):
    users = await db.pool.fetch("SELECT telegram_id, username FROM users")
    if users:
        msg = "\n".join([f"{u['telegram_id']} — @{u['username']}" for u in users])
        await message.answer(f"Пользователи:\n{msg}")
    else:
        await message.answer("Пользователей нет.")
