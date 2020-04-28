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
import aiohttp
from bs4 import BeautifulSoup
import base64


async def gcores():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))

    res, dt = await getgcores()

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'gcores';""")
        if len(values) == 0:
            await conn.execute(f"insert into rss values ('gcores','{dt})'")
        elif dt != values[0]["dt"]:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'gcores'")

        values = await conn.fetch(
            f"""select qid, dt from subs where rss = 'gcores'; """
        )

        for item in values:
            if item["dt"] != dt:
                await sendgcores(item["qid"], bot, res, dt)


async def getgcores():
    thing = fp.parse(r"http://172.18.0.1:1200/gcores/category/news")

    sp = BeautifulSoup(thing["entries"][0].summary, "lxml")

    pic = sp.find_all("img", attrs={"class": "newsPage_cover"})[0].attrs["src"]

    async with aiohttp.ClientSession() as sess:
        async with sess.get(pic, headers=headers) as resp:
            if resp.status != 200:
                session.finish("网络错误：" + str(resp.status))
            ShitBase64 = base64.b64encode(await resp.read())

    title = thing["entries"][0].title

    text = (
        title
        + "\n"
        + cq.image("base64://" + str(ShitBase64, encoding="utf-8"))
        + "传送门："
        + thing["entries"][0]["link"]
    )

    return text, title[: min(80, len(title))]


async def sendgcores(qid, bot, res=None, dt=None):
    if res == None or dt == None:
        res, dt = await getgcores()

    flg = 1

    async with db.pool.acquire() as conn:
        try:
            await bot.send_private_msg(user_id=qid, message=res)
            await conn.execute(
                f"""update subs set dt = '{dt}' where qid = {qid} and rss = 'gcores';"""
            )
        except CQHttpError:
            flg = 0
            await bot.send_group_msg(
                group_id=1037557679,
                message=unescape(cq.at(qid) + "貌似该资讯并没有发送成功，请尝试与我创建临时会话。"),
            )

    return flg
