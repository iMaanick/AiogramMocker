import datetime
import pprint
from typing import Any, Optional, Union
from unittest.mock import Mock

import pytest
from aiogram import Dispatcher, Bot
from aiogram.client.default import Default
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import TelegramMethod, AnswerCallbackQuery
from aiogram.types import Message, ReplyParameters, MessageEntity, LinkPreviewOptions, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, ForceReply, ReplyKeyboardMarkup, Chat

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format


class MainSG(StatesGroup):
    start = State()
    next = State()


async def on_click(event, button, manager: DialogManager) -> None:
    manager.middleware_data["usecase"]()
    await manager.event.bot.send_message(chat_id=1, text="12312312")
    await manager.next()


async def on_finish(event, button, manager: DialogManager) -> None:
    await manager.done()


async def second_getter(user_getter, **kwargs) -> dict[str, Any]:
    return {
        "user": user_getter(),
    }


dialog = Dialog(
    Window(
        Format("stub"),
        Button(Const("Button"), id="hello", on_click=on_click),
        state=MainSG.start,
    ),
    Window(
        Format("Next {user}"),
        Button(Const("Finish"), id="hello", on_click=on_finish),
        state=MainSG.next,
        getter=second_getter,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


class MyBot(Bot):
    def __init__(self, message_manager: MockMessageManager):
        self.message_manager = message_manager
        pass  # do not call super, so it is invalid bot, used only as a stub

    async def send_message(
            self,
            chat_id: Union[int, str],
            text: str,
            business_connection_id: Optional[str] = None,
            message_thread_id: Optional[int] = None,
            parse_mode: Optional[Union[str, Default]] = Default("parse_mode"),
            entities: Optional[list[MessageEntity]] = None,
            link_preview_options: Optional[Union[LinkPreviewOptions, Default]] = Default(
                "link_preview"
            ),
            disable_notification: Optional[bool] = None,
            protect_content: Optional[Union[bool, Default]] = Default("protect_content"),
            allow_paid_broadcast: Optional[bool] = None,
            message_effect_id: Optional[str] = None,
            reply_parameters: Optional[ReplyParameters] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
            ] = None,
            allow_sending_without_reply: Optional[bool] = None,
            disable_web_page_preview: Optional[Union[bool, Default]] = Default(
                "link_preview_is_disabled"
            ),
            reply_to_message_id: Optional[int] = None,
            request_timeout: Optional[int] = None,
    ) -> Message:
        message = Message(
            message_id=1,
            date=datetime.datetime.now(),
            chat=Chat(
                id=1,
                type='private'
            ),
            text=text
        )
        self.message_manager.sent_messages.append(message)
        return message

    @property
    def id(self):
        return 1

    async def __call__(
            self, method: TelegramMethod[Any],
            request_timeout: Optional[int] = None,
    ) -> Any:
        del request_timeout  # unused
        if isinstance(method, AnswerCallbackQuery):
            return True
        raise RuntimeError("Fake bot should not be used to call telegram")

    def __hash__(self) -> int:
        return 1

    def __eq__(self, other) -> bool:
        return self is other


@pytest.mark.asyncio
async def test_click():
    usecase = Mock()
    user_getter = Mock(side_effect=["Username"])
    dp = Dispatcher(
        usecase=usecase, user_getter=user_getter,
        storage=JsonMemoryStorage(),
    )
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())

    message_manager = MockMessageManager()
    client = BotClient(dp, bot=MyBot(message_manager))
    setup_dialogs(dp, message_manager=message_manager)

    # start
    await client.send("/start")
    first_message = message_manager.last_message()
    assert first_message.text == "stub"
    assert first_message.reply_markup
    user_getter.assert_not_called()

    # redraw
    # message_manager.reset_history()
    await client.send("whatever")

    first_message = message_manager.last_message()
    assert first_message.text == "stub"

    # click next
    # message_manager.reset_history()
    callback_id = await client.click(
        first_message, InlineButtonTextLocator("Button"),
    )

    message_manager.assert_answered(callback_id)
    usecase.assert_called()
    assert message_manager.sent_messages[-2].text == '12312312'
    second_message = message_manager.last_message()
    assert second_message.text == "Next Username"
    assert second_message.reply_markup.inline_keyboard
    user_getter.assert_called_once()

