from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
import asyncio
import asyncpg
from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from db import db
import cq
import feedparser as fp
import re

# num 第一个表示最获取的消息数，第二个表示在此基础上查看的消息数
# -1表示最大，-2表示到已读为止。


async def sendrss(
    qid: int, bot, source: str, ress=None, getfun=None, num=(-2, 3), session=None
):
    flg = 1

    async with db.pool.acquire() as conn:
        values = await conn.fetch(
            f"""select dt from subs where qid={qid} and rss='{source}';"""
        )
        if len(values) > 0:
            qdt = values[0]["dt"]
        else:
            qdt = None
        cnt = 0
        is_read = False
        if ress == None:
            ress = await getfun((num[0] if num[0] != -2 else -1))
        if num[0] == -2:
            for i in range(len(ress)):
                if ress[i][1] == qdt:
                    ress = ress[:i]
                    break
        if num[1] != -1:
            ress = ress[: min(len(ress), num[1])]

        success_dt = ""
        for res, dt in reversed(ress):
            if is_read == False and dt == qdt:
                is_read = True
            if num[1] != -1 and cnt >= num[1]:
                break

            see = ""
            try:
                is_r = is_read
                cnt += 1
                await bot.send_private_msg(user_id=qid, message="=" * 20)
                for text in res:
                    see = text
                    await bot.send_private_msg(
                        user_id=qid, message=("已读：\n" if is_r else "") + text
                    )
                    is_r = False
                success_dt = dt
            except CQHttpError:
                pass

        try:
            await bot.send_private_msg(user_id=qid, message="=" * 20)
        except CQHttpError:
            pass

        await bot.send_private_msg(user_id=qid, message=f"已发送 {cnt} 条「{source}」的资讯！咕噜灵波～(∠・ω< )⌒★")
        if success_dt != "":
            await conn.execute(
                f"""update subs set dt = '{success_dt}' where qid = {qid} and rss = '{source}';"""
            )

    return flg
