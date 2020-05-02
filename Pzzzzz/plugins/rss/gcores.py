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
from utils import *
import feedparser as fp
import re
from .utils import sendrss
import aiohttp
from bs4 import BeautifulSoup
import base64


async def gcores():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'gcores';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('gcores','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getgcores()

        _, dt = ress[0]

        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'gcores'")

        values = await conn.fetch(
            f"""select qid, dt from subs where rss = 'gcores'; """
        )

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "gcores", ress)


async def getgcores(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/gcores/category/news")

    cnt = 0

    ress = [
        (
            ["暂时没有新资讯哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
        )
    ]

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break
        sp = BeautifulSoup(item.summary, "lxml")

        pic = sp.find_all("img", attrs={"class": "newsPage_cover"})[0].attrs["src"]
        fd = re.search(r"\?", pic)
        if fd != None:
            pic = pic[: fd.span()[0]]

        async with aiohttp.ClientSession() as sess:
            pic = await sendpic(sess, pic)

        title = item.title

        text = (
            title + "\n" + ((pic + "\n") if pic != None else "") + "传送门：" + item["link"]
        )

        ress.append(([text], title[: min(80, len(title))]))
        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress
