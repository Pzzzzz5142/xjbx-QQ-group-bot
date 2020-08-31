from nonebot import on_command, CommandSession, get_bot
import json
from nonebot.message import escape as message_escape
from aiohttp import ClientSession
from nonebot.argparse import ArgumentParser
import cq

parm = {"type": "1", "s": "十年", "limit": 1}


@on_command("点歌", only_to_me=False)
async def _(session: CommandSession):
    msg = session.current_arg.strip()
    if msg == "":
        return
    parm["s"] = msg
    async with ClientSession() as sess:
        async with sess.get(
            "https://music.163.com/api/search/get/web", params=parm
        ) as resp:
            if resp.status != 200:
                session.finish("网络错误哦，咕噜灵波～(∠・ω< )⌒★")
            ShitJson = await resp.read()
            ShitJson = json.loads(ShitJson)
            ShitJson = ShitJson["result"]["songs"][0]["id"]
            await session.send(
                cq.music("163", ShitJson), auto_escape=False,
            )

