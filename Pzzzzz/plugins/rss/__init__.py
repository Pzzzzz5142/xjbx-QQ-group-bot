from nonebot import on_command, CommandSession, on_startup, permission as perm
from nonebot.message import unescape
import asyncio
import asyncpg
from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
import yaml
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import cq
from utils import *
import feedparser as fp
import re
from .bcr import bcr
from .mrfz import mrfz


@nonebot.scheduler.scheduled_job("cron", hour="22", minute="0")
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))
    try:
        async with db.pool.acquire() as conn:
            await bot.send_group_msg(group_id=145029700, message=f"呐，今天手游玩了吗？")
    except CQHttpError:
        pass


@nonebot.scheduler.scheduled_job("cron", hour="5", minute="0")
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))
    try:
        async with db.pool.acquire() as conn:
            await bot.send_group_msg(
                group_id=145029700, message=f"Ciallo～(∠・ω< )⌒★，该起床肝手游了。"
            )
    except CQHttpError:
        pass


@nonebot.scheduler.scheduled_job("interval", minutes=20)
# @on_command("ce", only_to_me=False, shell_like=True)
async def rss():
    await bcr()
    await mrfz()


@on_command("ce", only_to_me=False, shell_like=True, permission=perm.SUPERUSER)
async def __(x):
    pass
