from nonebot import on_command, CommandSession, on_startup, permission
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
import base64
from PIL import Image
from io import BytesIO


@on_command(
    "getinfo",
    aliases={"info", "help", "帮助"},
    only_to_me=False,
    permission=permission.SUPERUSER,
)
async def generalhelp(session: CommandSession):
    # 获取设置了名称的插件列表
    plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))
    lk = requests.get(
        r"https://i.pixiv.cat/img-original/img/2015/08/09/00/14/34/51860312_p0.jpg"
    )
    ls = base64.b64encode(BytesIO(lk.content).read())
    lk.close()
    # print(ls)

    await session.send(unescape(cq.image("base64://" + str(ls, encoding="utf-8"))))
    await session.send(
        unescape(
            cq.image(
                r"https://i.pixiv.cat/img-original/img/2015/08/09/00/14/34/51860312_p0.jpg"
            )
        )
    )

    arg = session.current_arg_text.strip().lower()
    if not arg:
        # 如果用户没有发送参数，则发送功能列表
        await session.send(
            "我现在支持的功能有：\n\n" + "\n".join(p.name for p in plugins if p.name != None)
        )
        return

    # 如果发了参数则发送相应命令的使用帮助
    for p in plugins:
        if p.name.lower() == arg:
            await session.send(p.usage)
