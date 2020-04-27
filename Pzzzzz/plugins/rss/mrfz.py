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
from utils import *


async def mrfz():
    bot = nonebot.get_bot()

    res, dt = await getmrfz()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'mrfz';""")
        if len(values) == 0:
            await conn.execute(f"insert into rss values ('mrfz','{dt}')")
        elif dt != values[0]["dt"]:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'mrfz'")
            try:
                await bot.send_group_msg(
                    group_id=145029700,
                    message="「明日方舟」有新公告啦！输入 rss mrfz 即可查看！已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'mrfz'; """)
        for item in values:
            if item["dt"] != dt:
                await sendmrfz(item["qid"], bot, res, dt)


def dfs(thing):
    if isinstance(thing, str):
        return thing
    if thing.name == "br":
        return "<br/>"
    res = ""
    for item in thing.contents:
        res += dfs(item)
    return res


async def getmrfz():
    thing = fp.parse(r"http://172.18.0.1:1200/arknights/news")

    sp = BeautifulSoup(thing["entries"][0].summary, "lxml")

    pp = sp.find_all("p")

    res = "标题：" + thing["entries"][0]["title"] + "\n\n"
    for i in pp:
        ans = dfs(i)
        if ans != "":
            res += (ans if ans != "<br/>" else "") + "\n"

    return res, thing["entries"][0]["published"]


async def sendmrfz(qid, bot, res=None, dt=None):
    if res == None or dt == None:
        res, dt = await getmrfz()

    flg = 1

    async with db.pool.acquire() as conn:
        try:
            await bot.send_private_msg(user_id=qid, message=res)
            await conn.execute(
                f"""update subs set dt = '{dt}' where qid = {qid} and rss = 'mrfz';"""
            )
        except CQHttpError:
            flg = 0
            await bot.send_group_msg(
                group_id=145029700,
                message=unescape(cq.at(qid) + "貌似公告并没有发送成功，请尝试与我创建临时会话。"),
            )

    return flg
