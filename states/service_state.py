from aiogram.fsm.state import State,StatesGroup

class UpdateSatete(StatesGroup):
    
    service_id = State()
    name = State()
    duration = State()
    price = State()