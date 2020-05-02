import feedparser as fp
import re
from bs4 import BeautifulSoup
import os.path as path
from nonebot import on_command, CommandSession, on_startup
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
from .utils import sendrss
from utils import *


async def mrfz():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'mrfz';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('mrfz','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getmrfz()

        _, dt = ress[0]

        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'mrfz'")
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP,
                    message=f"「{doc['mrfz']}」有新公告啦！输入 rss mrfz 即可查看！已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'mrfz'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "mrfz", ress)


def dfs(thing):
    if isinstance(thing, str):
        return thing
    if thing.name == "br":
        return "<br/>"
    res = ""
    for item in thing.contents:
        res += dfs(item)
    return res


async def getmrfz(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/arknights/news")

    ress = [
        (
            ["暂时没有有用的新公告哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
        )
    ]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        sp = BeautifulSoup(item.summary, "lxml")

        pp = sp.find_all("p")

        res = "标题：" + item["title"] + "\n"
        for i in pp:
            ans = dfs(i)
            if ans != "":
                res += "\n" + (ans if ans != "<br/>" else "")

        if "封禁" in res:
            continue

        ress.append(([res], item["published"]))

    if len(ress) > 1:
        ress = ress[1:]

    return ress
