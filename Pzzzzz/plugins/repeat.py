from nonebot import on_natural_language, NLPSession
from math import exp
from random import random

tjmp = {}


def sigmoid(num):
    if num < 1:
        return -1
    num -= 1
    return 1 / (1 + exp(-num))


@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    msg = session.msg.strip(" ")
    global tjmp
    if session.event.detail_type != "group":
        return
    if session.event.group_id not in tjmp:
        tjmp[session.event.group_id] = [0, "", ""]
    now = tjmp[session.event.group_id]
    if msg == "" or msg == now[1]:
        now[0] = 0
        return
    if msg == now[2]:
        now[0] += 1
    now[2] = msg
    if random() < sigmoid(now[0]):
        now[1] = msg
        await session.send(msg)
        now[0] = 0
        return
