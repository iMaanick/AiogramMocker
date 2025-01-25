import asyncio
import pprint

import pytest
from aiogram import Dispatcher
from aiogram_dialog.test_tools import MockMessageManager, BotClient
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage

from app.mock_bot import MockBot
from tests.test_groosha.handlers import common, ordering_food, ordering_drinks


@pytest.mark.asyncio
async def test_click():
    dp = Dispatcher(
        storage=JsonMemoryStorage(),
    )
    dp.include_routers(common.router, ordering_food.router, ordering_drinks.router)

    message_manager = MockMessageManager()
    client = BotClient(dp, bot=MockBot(message_manager))
    # setup_dialogs(dp, message_manager=message_manager)

    await client.send("/start")
    first_message = message_manager.last_message()
    first_message_text = ("Выберите, что хотите заказать: "
                          "блюда (/food) или напитки (/drinks).")
    assert first_message.text == first_message_text

    await client.send("/food")
    second_message = message_manager.last_message()
    second_message_text = "Выберите блюдо:"
    assert second_message.text == second_message_text

    await client.send("Спагетти")
    third_message = message_manager.last_message()
    third_message_text = "Спасибо. Теперь, пожалуйста, выберите размер порции:"
    assert third_message.text == third_message_text

    await client.send("Большую")
    fourth_message = message_manager.last_message()
    fourth_message_text = (f"Вы выбрали большую порцию спагетти.\n"
                           f"Попробуйте теперь заказать напитки: /drinks")
    assert fourth_message.text == fourth_message_text

    await client.send("/drinks")
    await asyncio.sleep(0.03)
    fifth_message = message_manager.last_message()
    pprint.pprint(fifth_message.reply_markup)
    fifth_message_text = f"Сообщение с кнопкой"
    assert fifth_message.text == fifth_message_text

    callback_id = await client.click(
        fifth_message, InlineButtonTextLocator("Кнопка"),
    )
    sixth_message = message_manager.last_message()
    sixth_message_text = "Кнопка работает"
    assert sixth_message.text == sixth_message_text
