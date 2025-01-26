import asyncio

import pytest
from aiogram import Dispatcher

from app.bot_client import BotClient
from app.keyboard import InlineButtonTextLocator
from app.memory_storage import JsonMemoryStorage
from app.mock_bot import MockBot
from app.mock_message_manager import MockMessageManager
from app.test_groosha.handlers import test_button
from app.test_groosha.handlers import ordering_food, common


@pytest.mark.asyncio
async def test_groosha():
    dp = Dispatcher(
        storage=JsonMemoryStorage(),
    )
    dp.include_routers(common.router, ordering_food.router, test_button.router)

    message_manager = MockMessageManager()
    client = BotClient(dp, bot=MockBot(message_manager), user_id=5, chat_id=5)
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
    fifth_message_text = f"Сообщение с кнопкой"
    assert fifth_message.text == fifth_message_text

    await client.click(
        fifth_message, InlineButtonTextLocator("Кнопка"),
    )
    sixth_message = message_manager.last_message()
    sixth_message_text = "Кнопка работает"
    assert sixth_message.text == sixth_message_text

    assert message_manager.last_message_id == 6

    await client.click(
        sixth_message, InlineButtonTextLocator("Изменить"),
    )
    sixth_message = message_manager.last_message()
    sixth_message_text = "Измененный текст"
    assert sixth_message.text == sixth_message_text
    assert sixth_message.message_id == 6
