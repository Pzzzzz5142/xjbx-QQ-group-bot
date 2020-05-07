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


@on_command("活动预测", aliases={"activity", "act"}, only_to_me=False)
async def tulai(session: CommandSession):
    await session.send(unescape(cq.image("activity.jpg")))


@on_command("h3", aliases={"H3"}, only_to_me=False)
async def tulai(session: CommandSession):
    await session.send(unescape(cq.image("H3.jpg")))


@on_command("孤儿", aliases={"装备"}, only_to_me=False)
async def tulai(session: CommandSession):
    await session.send(unescape(cq.image("gl.jpg")))


@on_command("ghz", aliases={"公会战"}, only_to_me=False)
async def tulai(session: CommandSession):
    await session.send(unescape(cq.image("ghz.jpg")))
