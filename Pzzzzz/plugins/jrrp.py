from nonebot import on_command, CommandSession, on_startup, permission
from nonebot.message import unescape
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
from nonebot.log import logger
import cq
from db import db
import datetime
from random import randint


@on_command("jrrp", only_to_me=False)
async def jrrp(session: CommandSession):
    today = datetime.date.today()
    ans = -1
    async with db.pool.acquire() as conn:
        values = await conn.fetch(
            """ select dt, rand from jrrp where qid={};""".format(session.event.user_id)
        )
        if len(values) == 0:
            ans = randint(0, 100)
            await conn.execute(
                """ insert into jrrp values ({},'{}',{})""".format(
                    session.event.user_id, today, ans
                )
            )
        else:
            values = values[0]
            if values["dt"] != today:
                ans = randint(0, 100)
                await conn.execute(
                    """update jrrp set rand = {},dt='{}'  where qid={};""".format(
                        ans, today, session.event.user_id
                    )
                )
            else:
                ans = values["rand"]

    session.finish(unescape(cq.at(session.event.user_id) + "今天的人品为：{} 哦！".format(ans)))
