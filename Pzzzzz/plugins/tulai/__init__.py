from nonebot import on_command, CommandSession, on_startup, permission
from nonebot.message import unescape
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
from nonebot.log import logger
import cq
from db import db
import datetime
from random import randint


@on_command("图来", only_to_me=False)
async def tulai(session: CommandSession):
    await session.send(unescape(cq.image("activity.jpg")))
