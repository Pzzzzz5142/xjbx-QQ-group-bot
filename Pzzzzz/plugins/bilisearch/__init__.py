from re import S
from typing import NoReturn
from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime, timedelta
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
from nonebot.log import logger
import cq
import requests
import os.path as path
from .utils import packbili
import aiohttp
from bs4 import BeautifulSoup
import re
from utils import headers

url = r"http://api.bilibili.com/x/web-interface/search/all/v2"
parm = {"keyword": "Halo"}
trans = {"bili_user": "Up主"}

__plugin_name__ = "bili search"


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

    parm["keyword"] = keyword

    async with aiohttp.ClientSession() as sess:
        async with sess.get(url, headers=headers, params=parm) as resp:
            if resp.status != 200:
                session.finish("网络错误：" + str(resp.status))
            ShitJson = await resp.json()
    ShitJson = ShitJson["data"]

    lmt = min(
        lmt,
        ShitJson["numResults"] % ShitJson["pagesize"]
        + (
            ShitJson["pagesize"]
            if ShitJson["numResults"] % ShitJson["pagesize"] == 0
            and ShitJson["numResults"] != 0
            else 0
        ),
    )

    if lmt == 0:
        session.finish("未搜索到「{}」的相关内容。".format(keyword))

    if lmt != 1:
        await session.send("以下是「{}」的搜索结果".format(keyword))

    cnt = 0

    try:
        for data in ShitJson["result"]:
            tp = data["result_type"]
            for thing in data["data"]:
                cnt += 1
                if tp == "bili_user":
                    print(
                        packbili(
                            r"https://space.bilibili.com/" + str(thing["mid"]),
                            thing["uname"] + "的空间",
                            "https:" + thing["upic"],
                            thing["usign"],
                        )
                    )
                    await session.send(
                        packbili(
                            r"https://space.bilibili.com/" + str(thing["mid"]),
                            thing["uname"] + "的空间",
                            "https:" + thing["upic"],
                            thing["usign"],
                        ),

                    )
                elif tp == "video":
                    await session.send(
                        packbili(
                            thing["arcurl"],
                            thing["title"],
                            "https:" + thing["pic"],
                            thing["description"],
                        ),
                    )
                elif tp == "media_bangumi":
                    await session.send(
                        packbili(
                            thing["url"],
                            thing["title"],
                            "https:" + thing["cover"],
                            f"番剧哦！这事番剧！\\n全 {thing['ep_size']} 集哦哦哦！",
                        )
                    )
                elif tp == "web_game":
                    await session.send(
                        packbili(
                            thing["game_link"],
                            thing["game_name"],
                            thing["game_icon"],
                            thing["summary"],
                        )
                    )
                else:
                    cnt -= 1
                if cnt >= lmt:
                    raise Exception
    except Exception:
        pass

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
