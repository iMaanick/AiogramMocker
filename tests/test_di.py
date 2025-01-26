import pytest
from aiogram import Dispatcher

from app.bot_client import BotClient
from app.memory_storage import JsonMemoryStorage
from app.mock_bot import MockBot
from app.mock_message_manager import MockMessageManager
from app.test_di import start_cmd
from app.test_di.start_cmd import DB


class MockDB(DB):
    def get_data(self) -> str:
        return 'fake data'


@pytest.mark.asyncio
async def test_di():
    dp = Dispatcher(
        storage=JsonMemoryStorage(),
        database=MockDB()
    )
    dp.include_routers(start_cmd.router)

    message_manager = MockMessageManager()
    client = BotClient(dp, bot=MockBot(message_manager), user_id=5, chat_id=5)

    await client.send("/start")
    first_message = message_manager.last_message()
    first_message_text = 'fake data'
    assert first_message.text == first_message_text
