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


async def hpoi():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'hpoi';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('hpoi','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await gethpoi()

        _, dt = ress[0]
        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'hpoi'")
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP,
                    message=f"「{doc['hpoi']}」有新公告啦！\n输入 rss hpoi 即可查看！\n输入 订阅 hpoi 即可订阅！（注意订阅后的空格哦！）\n已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'hpoi'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "hpoi", ress)


async def gethpoi(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/hpoi/info/all")

    ress = [
        (
            ["暂时没有有用的新咨询哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
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
                x = transtime(content[:16], "%Y-%M-%D %H:%M:%S")
            tm = x if tm == None or tm < x else tm

        ress.append((text, tm))

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
