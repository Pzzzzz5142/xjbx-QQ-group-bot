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
from .utils import sendrss
import feedparser as fp
import re


async def pprice():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'pprice';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('pprice','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getpprice()

        res, dt = ress[0]
        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'pprice'")
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP, message=res,
                )
            except CQHttpError:
                pass

        values = await conn.fetch(
            f"""select qid, dt from subs where rss = 'pprice'; """
        )

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "pprice", ress)


async def getpprice(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/pork-price")

    ress = [(["暂时没有猪肉价格哦！"], thing["entries"][0]["id"])]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break
        ress.append(([item["title"]], item["id"]))

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress
