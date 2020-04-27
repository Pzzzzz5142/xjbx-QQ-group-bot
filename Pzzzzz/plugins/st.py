from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime
import nonebot
import asyncio
import asyncpg
import aiohttp
from aiocqhttp.exceptions import Error as CQHttpError
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import re
from utils import *
import cq

url = r"https://saucenao.com/search.php"

data = {"db": "999", "output_type": "2", "numres": "3", "url": None}


@on_command("st", aliases={}, only_to_me=False)
async def st(session: CommandSession):

    purl = session.get("url", prompt="发送你想搜的图吧！")

    res = await sauce(purl)

    session.finish(unescape(res))


@st.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return

    if len(session.current_arg_images) == 0:
        session.finish("未找到消息中的图片，搜索结束！")

    session.state["url"] = session.current_arg_images[0]


async def sauce(purl: str) -> str:

    data["url"] = purl

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=data, headers=headers) as resp:
            if resp.status != 200:
                return "错误：" + str(resp.status)
            ShitJson = await resp.json()

    if len(ShitJson["results"]) == 0:
        return "啥也没搜到"

    try:
        murl = list(ShitJson["results"][0]["data"]["ext_urls"][0])
        for i in range(5):
            murl.insert(randint(0, len(murl)), "🐎")
        murl = "".join(murl)
    except:
        murl = ""

    return (
        cq.image(ShitJson["results"][0]["header"]["thumbnail"])
        + (
            f"\n标题：{ShitJson['results'][0]['data']['title']}"
            if "title" in ShitJson["results"][0]["data"]
            else ""
        )
        + (
            f"\nsource：{ShitJson['results'][0]['data']['source']}"
            if "source" in ShitJson["results"][0]["data"]
            else ""
        )
        + (
            f"\n日文名：{ShitJson['results'][0]['data']['jp_name']}"
            if "jp_name" in ShitJson["results"][0]["data"]
            else ""
        )
        + (
            f"\npixiv id: {ShitJson['results'][0]['data']['pixiv_id']}\n画师: {ShitJson['results'][0]['data']['member_name']}\n画师id: {ShitJson['results'][0]['data']['member_id']}"
            if "pixiv_id" in ShitJson["results"][0]["data"]
            else ""
        )
        + (f"\n来源（请复制到浏览器中打开，不要直接打开）：\n{murl}" if murl != "" else "")
        + "\n相似度："
        + str(ShitJson["results"][0]["header"]["similarity"])
        + "%"
    )
