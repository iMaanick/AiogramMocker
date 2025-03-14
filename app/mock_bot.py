import datetime
from copy import deepcopy
from typing import Union, Optional, Any

from aiogram import Bot
from aiogram.client.default import Default
from aiogram.methods import TelegramMethod, AnswerCallbackQuery, SendMessage
from aiogram.types import MessageEntity, LinkPreviewOptions, ReplyParameters, InlineKeyboardMarkup, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, ForceReply, Message, Chat
from aiogram_dialog.test_tools import MockMessageManager


class MockBot(Bot):
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
        self.message_manager.last_message_id += 1
        if isinstance(reply_markup, ReplyKeyboardRemove) or isinstance(reply_markup, ReplyKeyboardMarkup):
            message = Message(
                message_id=self.message_manager.last_message_id,
                date=datetime.datetime.now(),
                chat=Chat(
                    id=chat_id,
                    type='private'
                ),
                text=text,
            )
        else:
            message = Message(
                message_id=self.message_manager.last_message_id,
                date=datetime.datetime.now(),
                chat=Chat(
                    id=chat_id,
                    type='private'
                ),
                text=text,
                reply_parameters=reply_parameters,
                reply_markup=deepcopy(reply_markup)
            )
        self.message_manager.sent_messages.append(message)
        return message

    async def edit_message_text(
        self,
        text: str,
        business_connection_id: Optional[str] = None,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[Union[str, Default]] = Default("parse_mode"),
        entities: Optional[list[MessageEntity]] = None,
        link_preview_options: Optional[Union[LinkPreviewOptions, Default]] = Default(
            "link_preview"
        ),
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        disable_web_page_preview: Optional[Union[bool, Default]] = Default(
            "link_preview_is_disabled"
        ),
        request_timeout: Optional[int] = None,
    ) -> Union[Message, bool]:
        """
        Edit the text of a previously sent message.
        """
        # Check if message_id is provided and find the message in sent_messages
        if message_id is None:
            raise ValueError("message_id must be specified to edit a message.")

        # Locate the original message in the sent messages list
        original_message_index = next(
            (
                index
                for index, msg in enumerate(self.message_manager.sent_messages)
                if msg.message_id == message_id
            ),
            None,
        )

        if original_message_index is None:
            raise ValueError(f"Message with message_id {message_id} not found.")

        # Retrieve the original message
        original_message = self.message_manager.sent_messages[original_message_index]

        # Create a new message with updated text and other optional parameters
        updated_message = Message(
            message_id=original_message.message_id,
            date=original_message.date,  # Preserve original date
            chat=original_message.chat,  # Preserve original chat
            text=text,  # Update the text
            reply_markup=reply_markup or original_message.reply_markup,
            entities=entities or original_message.entities,
        )

        # Replace the original message in the list with the updated message
        self.message_manager.sent_messages[original_message_index] = updated_message

        # Return the updated message
        return updated_message

    @property
    def id(self):
        return 1

    async def __call__(
            self, method: TelegramMethod[Any],
            request_timeout: Optional[int] = None,
    ) -> Any:
        del request_timeout  # unused
        # print(method)
        # print(f"Called method: {type(method).__name__}")
        if isinstance(method, SendMessage):
            return await self.send_message(
                chat_id=method.chat_id,
                text=method.text,
                business_connection_id=method.business_connection_id,
                message_thread_id=method.message_thread_id,
                parse_mode=method.parse_mode,
                entities=method.entities,
                link_preview_options=method.link_preview_options,
                disable_notification=method.disable_notification,
                protect_content=method.protect_content,
                allow_paid_broadcast=method.allow_paid_broadcast,
                message_effect_id=method.message_effect_id,
                reply_parameters=method.reply_parameters,
                reply_markup=method.reply_markup,
                allow_sending_without_reply=method.allow_sending_without_reply,
                disable_web_page_preview=method.disable_web_page_preview,
                reply_to_message_id=method.reply_to_message_id,
            )
        if isinstance(method, AnswerCallbackQuery):
            return True
        raise RuntimeError("Fake bot should not be used to call telegram")

    def __hash__(self) -> int:
        return 1

    def __eq__(self, other) -> bool:
        return self is other
