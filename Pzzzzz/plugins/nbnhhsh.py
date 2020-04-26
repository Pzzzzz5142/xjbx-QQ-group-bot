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

url = r"https://lab.magiconch.com/api/nbnhhsh/guess"

headers = {"content-type": "application/json"}


@on_command("hhsh", aliases={}, only_to_me=False, shell_like=True)
async def setu(session: CommandSession):
    for i in session.argv:
        res = await query(i)
        for j in res:
            await session.send(j)


async def query(someShit):
    data = json.dumps({"text": someShit})

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=str(data)) as resp:
            if resp.status != 200:
                return ["错误：" + str(resp.status)]
            ShitJson = await resp.json()

    ans = []
    for RealShit in ShitJson:
        re = ""
        try:
            for i in RealShit["trans"]:
                re += i + "\n"
        except:
            for i in RealShit["inputting"]:
                re += i + "\n"
        re = re[:-1]
        if re == "":
            ans.append(f"没有查到 {RealShit['name']} 的相关结果")
        else:
            ans.append(
                f"""{RealShit['name']} 可能是：
{re}"""
            )

    return ans
