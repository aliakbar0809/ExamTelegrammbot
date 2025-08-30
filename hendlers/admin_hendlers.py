from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from database.user import User
from config import db
from database.service import Service
from database.queueEntry import QueueEntry
from keyboards.admin_keyboards import admin_keyboard
from states.service_state import UpdateSatete


from states.admin_states import AdminStates

admin_router = Router()

@admin_router.message(Command('start'))
async def start_handler(msg:Message):
    u1 = User(msg.from_user.id,msg.from_user.username,msg.from_user.full_name, db)
    user = await u1.get_user()
    if not user:
        await u1.save()
    
    if await u1.check_status():
        await msg.answer('Hello admin', reply_markup=admin_keyboard)
    else:
        from keyboards.user_keyboards import user_keyboard
        await msg.answer('Привет пользователь вот твое меню:', reply_markup=user_keyboard)

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

@admin_router.message(lambda a: a.text == '📋 Посмотреть услуги')
async def view_services_text_handler(msg: Message):
    
    service = await Service.get_all_service(db)
    print(service)

    for s in service:
        caption = (
            f"{s['id']}\n"
            f"{s['name']}\n"
            f"Время обслуживания: {s['duration']}\n"
            f"Цена: {s['price']}"
        )
        keybord = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='❌ Удалить услугу',callback_data=f'delete-{s['id']}'),
            InlineKeyboardButton(text='✅ Обновить услугу',callback_data=f'update-{s['id']}')]]
        )

        await msg.answer(caption=caption,reply_markup=keybord)



@admin_router.callback_query(F.data.contains('delete-'))
async def delete_product(clb: CallbackQuery):
    service_id = int(clb.data.split('-')[1])
    
    await Service.delete_service(db,service_id)
    await clb.answer('❌ Продукт удален')
    await clb.message.delete()

@admin_router.callback_query(F.data.contains('update-'))
async def hendler(clb:CallbackQuery,state:FSMContext):
    service_id = int(clb.data.split('-')[1])
    await state.set_state(UpdateSatete.name)
    await state.update_data(service_id=service_id)

    await clb.message.answer('Введите новое название прически: ')
    await state.set_state(UpdateSatete.name)

@admin_router.message(UpdateSatete.name)
async def new_name(msg:Message,state:FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer('Введите новое время обслуживания: ')
    await state.set_state(UpdateSatete.duration)

@admin_router.message(UpdateSatete.duration)
async def new_duration(msg:Message,state:FSMContext):
    await state.update_data(new_duration=msg.text)
    await msg.answer('Введите новый ценник стрижки: ')
    await state.set_state(UpdateSatete.price)

@admin_router.message(UpdateSatete.price)
async def new_price(msg:Message,state:FSMContext):
    data = await state.get_data()

    service = Service(
        name=data["name"],
        new_duration=data["duration"],
        price=data["price"],
        db=db  
    )
    await service.save()
    await msg.answer("✅ Услуга успешно обновлена: ", reply_markup=admin_keyboard)
    await state.clear()



@admin_router.message()
async def hendler(msg:Message):
    print(msg.chat.id)

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
