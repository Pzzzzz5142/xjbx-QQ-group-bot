from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
from nonebot.log import logger
from db import db
import cq
import requests
import os.path as path
import json
import aiohttp
from bs4 import BeautifulSoup
import re

url = r"https://search.bilibili.com/all?keyword="


@on_command("bilibili", aliases={"bili", "哔哩哔哩"}, only_to_me=False)
async def bilibili(session: CommandSession):

    keyword = session.get("kw", prompt="请输入你想搜索的内容！")
    if "lmt" in session.state:
        lmt = session.state["lmt"]
    else:
        if session.event.detail_type != "private":
            lmt = 1
        else:
            lmt = 5

    async with aiohttp.ClientSession() as sess:
        async with sess.get(url + keyword, headers=headers) as resp:
            if resp.status != 200:
                session.finish("网络错误：" + str(resp.status))
            ShitHtml = await resp.text()

    sp = BeautifulSoup(ShitHtml, "lxml")

    title = sp.find_all("a", attrs={"class": "title"})

    lmt = min(lmt, len(title))

    if lmt == 0:
        session.finish("未搜索到「{}」的相关内容。".format(keyword))

    if lmt != 1:
        await session.send("以下是「{}」的搜索结果".format(keyword))

    for i in range(lmt):
        res = ""
        if "https" not in title[i].attrs["href"]:
            lk = "https:" + title[i].attrs["href"]
        else:
            lk = title[i].attrs["href"]
        res = ""
        if "bangumi" in title[i].attrs["href"]:
            lk = re.findall(r"^https.*?md[0-9]*", lk)[0]
            num = re.findall(r"media/md[0-9]*", lk)[0]
            num = num[len(r"media/md") :]
            res = "\n该番剧的编号为：" + num
        if "?from=search" in lk:
            lk = lk[: -len("?from=search")]
        if "space" in lk:
            tp = "UP主"
            res += "\n该up主的 uid 为：" + re.findall("[0-9]+", lk)[0]
        elif "biligame" in lk:
            tp = "游戏"
        else:
            tp = "视频标题"
        await session.send("{}：{}\n链接：{}".format(tp, title[i].attrs["title"], lk) + res)

    if lmt > 2:
        session.finish("共返回 {} 条结果。".format(lmt))


@bilibili.args_parser
async def ___(session: CommandSession):
    arg = session.current_arg_text.strip()
    args = arg.split(" ")

    if args[0] == "-m":
        try:
            session.state["lmt"] = int(args[1])
        except:
            session.finish("参数传递错误！")
        arg = " ".join(args[2:])

    if session.is_first_run and arg == "":
        session.pause("请输入你想搜索的内容")

    if arg == "":
        session.pause("输入不能为空哦！")

    session.state["kw"] = arg
