from nonebot.message import unescape
import asyncio
import asyncpg
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.log import logger
from db import db
import cq
from utils import *
from .utils import sendrss
import feedparser as fp
import re
from bs4 import BeautifulSoup
import aiohttp


async def loli():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'loli';""")
        if len(values) == 0:
            raise Exception

        ress = await getloli()

        _, dt = ress[0]
        if dt != values[0]["dt"]:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'loli'")

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'loli'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "loli", ress)


async def getloli(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/hhgal")

    ress = [(["暂时没有新游戏哦！"], thing["entries"][0]["published"])]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        async with aiohttp.ClientSession() as sess:
            async with sess.get(item["link"], headers=headers) as resp:
                if resp.status != 200:
                    ShitHtml = "Html页面获取失败！错误码：" + str(resp.status)
                else:
                    ShitHtml = await resp.text()

        if ShitHtml[0] != "H":
            sp = BeautifulSoup(ShitHtml, "lxml")
            pic = sp.find_all("img", attrs={"title": "点击放大"})[0].attrs["src"]
        else:
            pic = ""

        pic = (cq.image(pic) + "\n") if pic != "" else pic

        text = [item.title + "\n" + pic + "链接：" + hourse(item["link"])]

        ress.append((text, item["published"]))

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress
