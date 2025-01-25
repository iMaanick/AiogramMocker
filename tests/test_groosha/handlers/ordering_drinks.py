from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(StateFilter(None), Command("drinks"))
async def cmd_food(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Кнопка",
        callback_data="button")
    )
    await message.answer(
        "Сообщение с кнопкой",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "button")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("Кнопка работает")
