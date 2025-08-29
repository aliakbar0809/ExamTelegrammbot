from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import db
from database.user import User
from database.service import Service
from database.queueEntry import QueueEntry
from keyboards.user_keyboards import user_keyboard, cancel_queue_kb
from keyboards.admin_keyboards import admin_keyboard
from states.user_states import UserStates

user_router = Router()

@user_router.message(Command("start"))
async def register_user(message: Message):
    
    user_data = await db.pool.fetchrow("SELECT * FROM users WHERE telegram_id=$1", message.from_user.id)

    if not user_data:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            fullname=message.from_user.full_name,
            db=db
        )
        await user.save()
        user_data = await db.pool.fetchrow("SELECT * FROM users WHERE telegram_id=$1", message.from_user.id)

    
    if user_data["is_staff"]:
        await message.answer("Вы админ ✅", reply_markup=admin_keyboard)
    else:
        await message.answer("Добро пожаловать, вы зарегистрированы как пользователь 👤", reply_markup=user_keyboard)


@user_router.message(F.text == "📋 Посмотреть услуги")
async def view_services(message: Message):
    services = await Service("", 0, 0, db).get_all()
    if services:
        msg = "\n".join([f"{s['id']}. {s['name']} – {s['duration']} мин – {s['price']}₽" for s in services])
        await message.answer(f"Доступные услуги:\n{msg}")
    else:
        await message.answer("Пока нет доступных услуг.")


@user_router.message(F.text == "📝 Записаться в очередь")
async def join_queue(message: Message, state: FSMContext):
    await message.answer("Введите ID услуги и дату (YYYY-MM-DD):\nПример: 2, 2025-09-01")
    await state.set_state(UserStates.waiting_for_queue_data)


@user_router.message(UserStates.waiting_for_queue_data)
async def process_queue_data(message: Message, state: FSMContext):
    try:
        service_id, date_str = message.text.split(",")
        service_data = await Service("", 0, 0, db).get_by_id(int(service_id.strip()))
        if not service_data:
            await message.answer("Услуга не найдена.")
            await state.clear()
            return

        user_data = await db.pool.fetchrow("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
        if not user_data:
            await message.answer("Вы не зарегистрированы. Введите /start для регистрации.")
            await state.clear()
            return

        queue_entry = QueueEntry(
            user_id=user_data["id"],
            service=service_data["name"],
            scheduled_time=date_str.strip(),
            db=db
        )
        await queue_entry.save()
        await message.answer("Вы записаны в очередь!")
    except Exception as e:
        await message.answer(f"Ошибка при записи: {e}")
    await state.clear()


@user_router.message(F.text == "📅 Моя очередь")
async def my_queue(message: Message):
    user_data = await db.pool.fetchrow("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
    if not user_data:
        await message.answer("Вы не зарегистрированы.")
        return

    entry = await QueueEntry(user_id=user_data["id"], db=db).get_user_active_entry()
    if entry:
        await message.answer(
            f"Вы в очереди:\nУслуга: {entry['service']}\nДата: {entry['scheduled_time']}\nСтатус: {entry['status']}",
            reply_markup=cancel_queue_kb()
        )
    else:
        await message.answer("У вас нет активных записей.")


@user_router.callback_query(F.data == "cancel_my_entry")
async def cancel_entry(callback: CallbackQuery):
    user_data = await db.pool.fetchrow("SELECT id FROM users WHERE telegram_id=$1", callback.from_user.id)
    if not user_data:
        await callback.message.answer("Вы не зарегистрированы.")
        return
    await QueueEntry(user_id=user_data["id"], db=db).cancel_user_entry()
    await callback.message.edit_text("Запись отменена ❌")
