from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


class TestButton(StatesGroup):
    edit = State()


@router.message(StateFilter(None), Command("drinks"))
async def cmd_food(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Кнопка",
        callback_data="button")
    )
    await message.answer(
        "Сообщение с кнопкой",
        reply_markup=builder.as_markup()
    )
    await state.set_state(TestButton.edit)


@router.callback_query(F.data == "button")
async def send_message_by_button(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Изменить",
        callback_data="edit_button")
    )
    message = await callback.message.answer("Кнопка работает", reply_markup=builder.as_markup())
    await state.update_data(message_id=message.message_id)


@router.callback_query(F.data == "edit_button")
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.bot.edit_message_text(text='Измененный текст', message_id=data['message_id'])
