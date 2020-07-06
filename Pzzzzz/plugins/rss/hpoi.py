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
import aiohttp
from bs4 import BeautifulSoup


async def hpoi(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/hpoi/info/all")

    ress = [
        (
            ["暂时没有有用的新资讯哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
            "",
        )
    ]
    t_max_num = max_num
    max_num = -1

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        async with aiohttp.ClientSession() as session:
            async with session.get(item["link"]) as resp:
                if resp.status != 200:
                    return "Html页面获取失败！错误码：" + str(resp.status)
                ShitHtml = await resp.text()

            sp = BeautifulSoup(ShitHtml, "lxml")

            ShitTime = sp.find_all(class_="left-item-content")
            ShitAttr = sp.find(class_="table table-condensed info-box")

            ShitAttr = ShitAttr.find_all("tr")

            ShitPic = sp.find("a", class_="thumbnail fix-thumbnail-margin-10")["href"]
            ShitPic = await sendpic(session, ShitPic)

        tm = None
        text = ""

        for i in ShitAttr:
            x = dfs(i)
            if x != "" and x[0] != "外":
                text += x + "\n"
        text = [ShitPic, text[:-1]]

        for i in ShitTime:
            content = i.contents[0]
            content = content.strip()
            x = transtime(content, "%a %b %d %H:%M:%S %Z %Y 创建")
            if isinstance(x, str):
                x = transtime(content[:16], "%Y-%m-%d %H:%M")
            if not isinstance(x, str):
                tm = x if tm == None or tm < x else tm

        ress.append(
            (text, tm, item["link"] if "link" in item and item["link"] != "" else "",)
        )

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    ress.sort(key=lambda x: x[1], reverse=True)

    return ress[:t_max_num]


def dfs(x) -> str:
    if isinstance(x, str):
        x = x.strip()
        return x if x != "\n" else ""
    res = ""
    for i in x.contents:
        res += dfs(i)
    return res
