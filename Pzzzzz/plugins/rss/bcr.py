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


async def bcr():
    bot = nonebot.get_bot()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'bcr';""")
        if len(values) == 0:
            await conn.execute("""insert into rss values ('bcr','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]

        ress = await getbcr()

        _, dt = ress[0]
        if dt != db_dt:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'bcr'")
            try:
                await bot.send_group_msg(
                    group_id=bot.config.QGROUP,
                    message=f"「{doc['bcr']}」有新公告啦！输入 rss bcr 即可查看！已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'bcr'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "bcr", ress)


async def getbcr(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/bilibili/user/dynamic/353840826")

    ress = [(["暂时没有有用的新公告哦！"], thing["entries"][0]["published"])]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        if (
            ("封禁公告" in item.summary)
            or ("小讲堂" in item.summary)
            or ("中奖" in item.summary)
        ):
            continue

        fdres = re.match(r".*?<br>", item.summary, re.S)

        text = fdres.string[int(fdres.span()[0]) : fdres.span()[1] - len("<br>")]

        while len(text) > 1 and text[-1] == "\n":
            text = text[:-1]

        pics = re.findall(
            r"https://(?:(?!https://).)*?\.(?:jpg|jpeg|png|gif|bmp|tiff|ai|cdr|eps)\"",
            item.summary,
            re.S,
        )
        text = [text]

        async with aiohttp.ClientSession() as sess:
            for i in pics:
                i = i[:-1]
                pic = await sendpic(sess, i)
                if pic != None:
                    text.append(pic)
        ress.append((text, item["published"]))

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress
