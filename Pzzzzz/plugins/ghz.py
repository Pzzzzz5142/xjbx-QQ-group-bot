from nonebot.message import unescape
import asyncio
import asyncpg
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import cq
from nonebot import on_command, CommandSession, permission as perm
import feedparser as fp
from db import db
import aiohttp


@on_command("出刀")
async def cd(session: CommandSession):
    pass


@nonebot.scheduler.scheduled_job("cron", hour="22", minute="0")
async def _():
    async with db.pool.acquire() as conn:
        values = await conn.fetch("select gid from mg where ghz = true")
        bot = nonebot.get_bot()
        for item in values:
            item = item["gid"]
            try:
                await bot.send_group_msg(
                    group_id=int(item),
                    message=unescape(
                        unescape(cq.at("all")) + " Ciallo～(∠・ω< )⌒★，今天你出刀了吗？"
                    ),
                )
            except CQHttpError:
                pass


@on_command("提醒", aliases={"non"}, only_to_me=False, permission=perm.SUPERUSER)
async def tx(session: CommandSession):
    bot = nonebot.get_bot()
    try:
        await bot.send_group_msg(
            group_id=bot.config.QGROUP,
            message=unescape(unescape(cq.at("all")) + " Ciallo～(∠・ω< )⌒★，今天你出刀了吗？"),
        )
    except CQHttpError:
        pass

