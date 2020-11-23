from nonebot import on_natural_language, NLPSession
from math import exp
from random import random

from nonebot.command import call_command

tjmp = {}


def sigmoid(num):
    if num < 1:
        return -1
    num -= 3
    print(1 / (1 + exp(-num)))
    return 1 / (1 + exp(-num))


async def repeat(session: NLPSession):
    msg = session.msg.strip(" ")
    global tjmp
    if session.event.detail_type != "group":
        return
    if session.event.group_id not in tjmp:
        tjmp[session.event.group_id] = [0, "", "", 0]
    now = tjmp[session.event.group_id]
    try:
        if msg == now[2]:
            now[0] += 1
        if "pixiv" in msg and "rss " in msg and "r18" in msg:
            now[-1] += 1
        else:
            now[-1] = 0
            raise Exception
        if now[-1] > 3:
            await call_command(session.bot, session.event, "怜悯")
            now[-1] = 0
            raise Exception
    except:
        pass
    if msg == "" or msg == now[1] or msg != now[2]:
        now[0] = 1
        now[2] = msg
        return
    now[2] = msg
    if random() < sigmoid(now[0]):
        now[1] = msg
        await session.send(msg)
        now[0] = 0
        return

