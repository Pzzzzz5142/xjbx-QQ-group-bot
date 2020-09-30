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
import base64
import os.path as path


async def _loli():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'loli';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('loli','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getloli()

        _, dt = ress[0]
        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'loli'")

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'loli'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "loli", ress)


async def loli(max_num: int = -1):
    return None
    thing = fp.parse(r"http://172.18.0.1:1200/hhgal")

    ress = [
        (
            ["暂时没有新游戏哦！"],
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

        ShitHtml, pic = await anti_anti_bot(item["link"])

        pic = (pic + "\n") if pic != None else ""

        text = [item.title + "\n" + pic + "链接：" + hourse(item["link"])]

        ress.append(
            (
                text,
                item["published"],
                item["link"] if "link" in item and item["link"] != "" else "",
                item["title"],
            )
        )

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress


async def anti_anti_bot(url) -> str:
    def stringToHex(s) -> str:
        ans = ""
        for i in s:
            ans += format(ord(i), "x")
        return ans

    cookies = {}
    urlData = stringToHex(url)
    screenData = stringToHex("1280,720")
    cookies["srcurl"] = urlData
    text = ""
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return "Html页面获取失败！错误码：" + str(resp.status)
            text = await resp.text()
        if "YunSuoAutoJump" in text:
            async with session.get(url + "?security_verify_data=" + screenData) as resp:
                if resp.status != 200:
                    return "Html页面获取失败！错误码：" + str(resp.status)
                await resp.text()

            async with session.get(url) as resp:
                if resp.status != 200:
                    return "Html页面获取失败！错误码：" + str(resp.status)
                resp = await session.get(url)
                text = await resp.text()

            if text[0] != "H":
                sp = BeautifulSoup(text, "lxml")
                pic = sp.find_all("img", attrs={"title": "点击放大"})[0].attrs["src"]
            else:
                pic = ""
            pic = await sendpic(session, pic)
    return text, pic
