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
            raise Exception

        ress = await getgcores()

        _, dt = ress[0]

        if dt != values[0]["dt"]:
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
            thing["entries"][0].title[: min(80, len(thing["entries"][0].title))],
        )
    ]

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break
        sp = BeautifulSoup(item.summary, "lxml")

        pic = sp.find_all("img", attrs={"class": "newsPage_cover"})[0].attrs["src"]

        async with aiohttp.ClientSession() as sess:
            async with sess.get(pic, headers=headers) as resp:
                if resp.status != 200:
                    ShitBase64 = "图片加载失败！错误码：" + str(resp.status)
                else:
                    ShitBase64 = str(
                        base64.b64encode(await resp.read()), encoding="utf-8"
                    )

        title = item.title

        text = (
            title
            + "\n"
            + (
                cq.image("base64://" + ShitBase64)
                if ShitBase64[0] != "图"
                else ShitBase64
            )
            + "传送门："
            + item["link"]
        )

        ress.append(([text], title[: min(80, len(title))]))
        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress