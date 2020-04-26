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

    thing = fp.parse(r"http://172.18.0.1:1200/arknights/news")

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'mrfz';""")
        if len(values) == 0:
            await conn.execute(
                f"insert into rss values ('mrfz','{thing['entries'][0]['published']}')"
            )
        elif thing["entries"][0]["published"] != values[0]["dt"]:
            await conn.execute(
                f"update rss set dt = '{thing['entries'][0]['published']}' where id = 'mrfz'"
            )
        else:
            return
    sp = BeautifulSoup(thing["entries"][0].summary,"lxml")

    pp = sp.find_all("p")

    flg = 1
    res = ""
    for i in pp:
        if flg:
            flg = 0
            continue
        ch = i.next
        while ch != None:
            res += ch.string if ch.string != None else ""
            ch = ch.next_sibling
        res += "\n"
    pass

    try:
        await bot.send_group_msg(group_id=145029700, message=res)
    except CQHttpError:
        pass
