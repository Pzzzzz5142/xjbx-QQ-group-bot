import feedparser as fp
import re
from bs4 import BeautifulSoup, Comment
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


async def _bh3():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'bh3';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('bh3','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getbh3()

        _, dt = ress[0]

        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'bh3'")
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP,
                    message=f"「{doc['bh3']}」有新公告啦！\n输入 rss bh3 即可查看！\n输入 订阅 bh3 即可订阅！（注意订阅后的空格哦！）\n已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'bh3'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "bh3", ress)


def dfs(thing):
    if isinstance(thing, Comment):
        return ""
    if isinstance(thing, str):
        return thing
    if thing.name == "br":
        return "<br/>"
    res = ""
    for item in thing.contents:
        res += dfs(item)
    return res


async def bh3(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/mihoyo/bh3/latest")

    ress = [
        (
            ["暂时没有有用的新公告哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
            "",
            "",
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

        if "封禁" in res or "封号" in res:
            continue

        ress.append(
            (
                [res],
                item["published"],
                item["link"] if "link" in item and item["link"] != "" else "",
                item["title"],
            )
        )

    if len(ress) > 1:
        ress = ress[1:]

    return ress
