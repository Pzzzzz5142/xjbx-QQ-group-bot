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
from .utils import sendrss
from utils import *


def dfs(thing):
    if isinstance(thing, str):
        return thing
    if thing.name == "br":
        return "<br/>"
    res = ""
    for item in thing.contents:
        res += dfs(item)
    return res


async def mrfz(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/arknights/news")

    ress = [
        (
            ["暂时没有有用的新公告哦！"],
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

        sp = BeautifulSoup(item.summary, "lxml")

        pp = sp.find_all("p")

        res = "标题：" + item["title"] + "\n"
        for i in pp:
            ans = dfs(i)
            if ans != "":
                res += "\n" + (ans if ans != "<br/>" else "")

        if "封禁" in res:
            continue

        ress.append(
            (
                [res],
                item["published"],
                item["link"] if "link" in item and item["link"] != "" else "",
                item["title"],
            )
        )

    if len(ress) > 1:
        ress = ress[1:]

    return ress
