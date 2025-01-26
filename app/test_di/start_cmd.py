from abc import abstractmethod
from typing import Protocol

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


class DB(Protocol):
    @abstractmethod
    def get_data(self) -> str:
        raise NotImplementedError


class RealDB(DB):
    def get_data(self) -> str:
        return 'real data'


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, database: DB):
    data = database.get_data()
    await message.answer(
        text=data
    )
