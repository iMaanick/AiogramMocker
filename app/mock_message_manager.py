from copy import deepcopy
from datetime import datetime
from typing import Optional

from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, CallbackQuery, Message
from aiogram_dialog import ShowMode
from aiogram_dialog.api.entities import OldMessage, NewMessage
from aiogram_dialog.api.protocols import MessageNotModified, MessageManagerProtocol
from aiogram_dialog.test_tools.mock_message_manager import file_id, MEDIA_CLASSES, file_unique_id


class MockMessageManager(MessageManagerProtocol):
    def __init__(self):
        self.answered_callbacks: set[str] = set()
        self.sent_messages = []
        self.last_message_id = 0

    def reset_history(self):
        self.sent_messages.clear()
        self.answered_callbacks.clear()

    def assert_one_message(self) -> None:
        assert len(self.sent_messages) == 1

    def last_message(self) -> Message:
        return self.sent_messages[-1]

    def first_message(self) -> Message:
        return self.sent_messages[0]

    def one_message(self) -> Message:
        self.assert_one_message()
        return self.first_message()

    async def remove_kbd(
            self,
            bot: Bot,
            show_mode: ShowMode,
            old_message: Optional[OldMessage],
    ) -> Optional[Message]:
        if not old_message:
            return None
        if show_mode in (ShowMode.DELETE_AND_SEND, ShowMode.NO_UPDATE):
            return None
        assert isinstance(old_message, OldMessage)

        message = Message(
            message_id=old_message.message_id,
            date=datetime.now(),
            chat=old_message.chat,
            reply_markup=None,
        )
        self.sent_messages.append(message)
        return message

    async def answer_callback(
            self, bot: Bot, callback_query: CallbackQuery,
    ) -> None:
        self.answered_callbacks.add(callback_query.id)

    def assert_answered(self, callback_id: str) -> None:
        assert callback_id in self.answered_callbacks

    async def show_message(self, bot: Bot, new_message: NewMessage,
                           old_message: Optional[OldMessage]) -> OldMessage:
        assert isinstance(new_message, NewMessage)
        assert isinstance(old_message, (OldMessage, type(None)))
        if new_message.show_mode is ShowMode.NO_UPDATE:
            raise MessageNotModified

        message_id = self.last_message_id + 1
        self.last_message_id = message_id

        if new_message.media:
            contents = {
                "caption": new_message.text,
                new_message.media.type: MEDIA_CLASSES[new_message.media.type](
                    new_message.media,
                ),
            }
        else:
            contents = {
                "text": new_message.text,
            }

        message = Message(
            message_id=message_id,
            date=datetime.now(),
            chat=new_message.chat,
            reply_markup=deepcopy(new_message.reply_markup),
            **contents,
        )
        self.sent_messages.append(message)

        return OldMessage(
            message_id=message_id,
            chat=new_message.chat,
            text=new_message.text,
            media_id=(
                file_id(new_message.media)
                if new_message.media
                else None
            ),
            media_uniq_id=(
                file_unique_id(new_message.media)
                if new_message.media
                else None
            ),
            has_reply_keyboard=isinstance(
                new_message.reply_markup, ReplyKeyboardMarkup,
            ),
            business_connection_id=None,
        )
