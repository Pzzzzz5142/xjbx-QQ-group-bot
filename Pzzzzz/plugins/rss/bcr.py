from nonebot.message import unescape
import asyncio
import asyncpg
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import cq
from utils import *
from .utils import sendrss, rssBili
import feedparser as fp
import re
import aiohttp


async def _bcr():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'bcr';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('bcr','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getbcr()

        _, dt = ress[0]
        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'bcr'")
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP,
                    message=f"「{doc['bcr']}」有新公告啦！\n输入 rss bcr 即可查看！\n输入 订阅 bcr 即可订阅！（注意订阅后的空格哦！）\n已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'bcr'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "bcr", ress)


async def bcr(max_num: int = -1):
    return await rssBili(353840826, max_num)

