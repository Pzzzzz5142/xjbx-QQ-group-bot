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


async def bcr():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))

    res, dt = await getbcr()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'bcr';""")
        if len(values) == 0:
            await conn.execute(f"insert into rss values ('bcr',{dt})")
        elif dt != values[0]["dt"]:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'bcr'")
            try:
                await bot.send_group_msg(
                    group_id=145029700,
                    message="「公主链接 B服」有新公告啦！输入 rss bcr 即可查看！已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'bcr'; """)
        for item in values:
            if item["dt"] != dt:
                await sendbcr(item["qid"], bot, res, dt)


async def getbcr():
    thing = fp.parse(r"http://172.18.0.1:1200/bilibili/user/dynamic/353840826")

    cnt = 0

    while (
        ("封禁公告" in thing["entries"][cnt].summary)
        or ("小讲堂" in thing["entries"][cnt].summary)
    ) and (cnt < len(thing["entries"])):
        cnt += 1

    if cnt == len(thing["entries"]):
        return "暂时没有有用的新公告哦！", thing["entries"][0]["published"]

    fdres = re.match(r".*?<br>", thing["entries"][cnt].summary, re.S)

    text = fdres.string[int(fdres.span()[0]) : fdres.span()[1] - len("<br>")]

    if text[-1] != "\n":
        text += "\n"

    pics = re.findall(
        r"https://.*?\.(?:jpg|jpeg|png|gif|bmp|tiff|ai|cdr|eps)\"",
        thing["entries"][cnt].summary,
        re.S,
    )

    for i in pics:
        text += cq.image(i[:-1])

    return text, thing["entries"][0]["published"]


async def sendbcr(qid, bot, res=None, dt=None):
    if res == None or dt == None:
        res, dt = await getbcr()

    flg = 1

    async with db.pool.acquire() as conn:
        try:
            await bot.send_private_msg(user_id=qid, message=res)
            await conn.execute(
                f"""update subs set dt = '{dt}' where qid = {qid} and rss = 'bcr';"""
            )
        except CQHttpError:
            flg = 0
            await bot.send_group_msg(
                group_id=145029700,
                message=unescape(cq.at(qid) + "貌似公告并没有发送成功，请尝试与我创建临时会话。"),
            )

    return flg
