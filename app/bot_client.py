import uuid
from datetime import datetime
from typing import Optional, Union

from aiogram import Dispatcher, Bot
from aiogram.types import Chat, User, Message, Update, InlineKeyboardButton, CallbackQuery, ChatJoinRequest, \
    ChatMemberUpdated, ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember, ChatMemberRestricted, ChatMemberLeft, \
    ChatMemberBanned

from app.keyboard import InlineButtonLocator
from app.mock_bot import MockBot

ChatMember = Union[
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberRestricted,
    ChatMemberLeft,
    ChatMemberBanned,
]


class BotClient:
    def __init__(
            self,
            dp: Dispatcher,
            user_id: int = 1,
            chat_id: int = 1,
            chat_type: str = "private",
            bot: Optional[Bot] = None,
    ):
        self.chat = Chat(id=chat_id, type=chat_type)
        self.user = User(
            id=user_id, is_bot=False,
            first_name=f"User_{user_id}",
        )
        self.dp = dp
        self.last_update_id = 1
        self.last_message_id = 1
        self.bot = bot or MockBot()

    def _new_update_id(self):
        self.last_update_id += 1
        return self.last_update_id

    def _new_message_id(self):
        self.last_message_id += 1
        return self.last_message_id

    def _new_message(
            self, text: str, reply_to: Optional[Message],
    ):
        return Message(
            message_id=self._new_message_id(),
            date=datetime.fromtimestamp(1234567890),
            chat=self.chat,
            from_user=self.user,
            text=text,
            reply_to_message=reply_to,
        )

    async def send(self, text: str, reply_to: Optional[Message] = None):
        return await self.dp.feed_update(self.bot, Update(
            update_id=self._new_update_id(),
            message=self._new_message(text, reply_to),
        ))

    def _new_callback(
            self, message: Message, button: InlineKeyboardButton,
    ) -> CallbackQuery:
        if not button.callback_data:
            raise ValueError("Button has no callback data")
        return CallbackQuery(
            id=str(uuid.uuid4()),
            data=button.callback_data,
            chat_instance="--",
            from_user=self.user,
            message=message,
        )

    async def click(
            self, message: Message,
            locator: InlineButtonLocator,
    ) -> str:
        button = locator.find_button(message)
        if not button:
            raise ValueError(
                f"No button matching {locator} found",
            )

        callback = self._new_callback(message, button)
        await self.dp.feed_update(self.bot, Update(
            update_id=self._new_update_id(),
            callback_query=callback,
        ))
        return callback.id

    async def request_chat_join(self):
        return await self.dp.feed_update(self.bot, Update(
            update_id=self._new_update_id(),
            chat_join_request=ChatJoinRequest(
                chat=self.chat,
                from_user=self.user,
                date=datetime.fromtimestamp(1234567890),
                user_chat_id=self.user.id,
            ),
        ))

    async def my_chat_member_update(
            self, old_chat_member: ChatMember, new_chat_member: ChatMember,
    ):
        return await self.dp.feed_update(self.bot, Update(
            update_id=self._new_update_id(),
            my_chat_member=ChatMemberUpdated(
                chat=self.chat,
                from_user=self.user,
                date=datetime.fromtimestamp(1234567890),
                old_chat_member=old_chat_member,
                new_chat_member=new_chat_member,
            ),
        ))
