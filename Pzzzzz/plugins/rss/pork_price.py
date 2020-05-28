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

__rss_name__ = "pprice"


async def _pprice():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(
            f"""select dt from rss where id = '{__rss_name__}';"""
        )
        if len(values) == 0:
            await conn.execute(f"""insert into rss values ('{__rss_name__}','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getpprice()

        res, dt = ress[0]
        if dt == "Grab Rss Error!":
            logger.error(f"Grab Rss「{__rss_name__}」 Error!")
            return
        if dt != db_dt:
            await conn.execute(
                f"update rss set dt = '{dt}' where id = '{__rss_name__}'"
            )
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP, message=res[0],
                )
            except CQHttpError:
                pass

        values = await conn.fetch(
            f"""select qid, dt from subs where rss = '{__rss_name__}'; """
        )

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, __rss_name__, ress)


async def pprice(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/pork-price")

    ress = [
        (
            ["暂时没有猪肉价格哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
            "",
        )
    ]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break
        ress.append(
            (
                [item["title"]],
                item["title"],
                item["link"] if "link" in item and item["link"] != "" else "",
            )
        )

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress
