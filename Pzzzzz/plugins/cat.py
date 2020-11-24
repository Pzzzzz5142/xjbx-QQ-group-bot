import json
from nonebot import on_command, CommandSession
from nonebot.message import unescape, escape
import nonebot
import aiohttp
from aiocqhttp.exceptions import Error as CQHttpError
from utils import *
import cq
import random
from utils import imageProxy, imageProxy_cat, cksafe


@on_command("cat", only_to_me=False)
async def cat(session: CommandSession):
    p = None
    try:
        ls = session.current_arg_text.strip().split("-")
        _id = ls[0]
        _id = int(_id)
    except:
        session.finish("请输入正确格式的pid哦~~")
    try:
        p = ls[1]
        if p != "*":
            p = int(p)
            if p == 0:
                raise Exception
    except IndexError:
        pass
    except:
        session.finish("页码不对哦~~页码从0开始。。")
    await session.send(cq.reply(session.event.message_id) + "尝试发送中，。，。，。")
    pics = await catPixiv(_id, p)
    for pic in pics:
        await session.send(pic)
    if len(pics) > 2:
        session.finish("发送完毕！")
