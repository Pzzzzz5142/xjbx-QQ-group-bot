from nonebot import on_command, CommandSession, on_startup, permission as perm
from nonebot.message import unescape
import asyncio
import asyncpg
from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
import yaml
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import cq
from utils import doc
import feedparser as fp
import re
from .utils import sendrss, getrss
from .bcr import bcr, getbcr
from .mrfz import mrfz, getmrfz
from .gcores import gcores, getgcores
from .loli import loli, getloli


@nonebot.scheduler.scheduled_job("cron", hour="5", minute="0")
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))
    try:
        async with db.pool.acquire() as conn:
            await bot.send_group_msg(
                group_id=145029700, message=f"Ciallo～(∠・ω< )⌒★，早上好。"
            )
    except CQHttpError:
        pass


@nonebot.scheduler.scheduled_job("interval", minutes=20)
# @on_command("ce", only_to_me=False, shell_like=True)
async def __():
    await bcr()
    await mrfz()
    await gcores()


@on_command("rss", only_to_me=False)
async def rss(session: CommandSession):

    if session.state["ls"] == []:
        session.pause(
            "请输入你想「{0}」的资讯！\n输入 mrfz 代表 「明日方舟」\n输入 bcr 代表 「公主链接 B服」\n输入 gcores 代表 「机核网」\n如果有多个想{0}的资讯源可以在一行中输入多个并以空格分开！".format(
                "查看" if session.state["subs"] == 0 else "订阅"
            )
        )

    if session.state["subs"] == 1:
        async with db.pool.acquire() as conn:
            for _, item in session.state["ls"]:
                try:
                    await conn.execute(
                        """insert into subs values ({},'{}','{}')""".format(
                            session.event.user_id, -1, item
                        )
                    )
                    await session.send(f"「{doc[item]}」的资讯已添加订阅了！有新资讯发布时，会私信你哦！")
                except:
                    await session.send(f"你已经添加过「{doc[item]}」的资讯订阅啦！")

    elif "route" in session.state:
        bot = nonebot.get_bot()
        for rt in session.state["ls"]:
            resp = await sendrss(
                session.event.user_id, bot, "自定义路由", None, getrss, (1, 1), route=rt,
            )
            if resp and session.event.detail_type != "private":
                await session.send(
                    unescape(cq.at(session.event.user_id) + f"「{rt}」的资讯已私信，请查收。")
                )

    else:
        async with db.pool.acquire() as conn:
            bot = nonebot.get_bot()
            for item, nm in session.state["ls"]:
                resp = await sendrss(
                    session.event.user_id, bot, nm, None, item, (1, 1), session=session,
                )
                if resp and session.event.detail_type != "private":
                    await session.send(
                        unescape(
                            cq.at(session.event.user_id) + f"「{doc[nm]}」的资讯已私信，请查收。"
                        )
                    )


@rss.args_parser
async def ___(session: CommandSession):
    arg = session.current_arg_text.strip()
    args = arg.split(" ")
    args = [i for i in args if i != ""]

    if session.is_first_run:
        session.state["ls"] = []
        session.state["subs"] = 1 if (len(args) > 0 and args[0] == "-s") else 0
        if "-r" in args:
            args.remove("-r")
            if "-s" in args:
                session.finish("-s 和 -r 参数不能共存哦！")
            else:
                session.state["route"] = "ok"
            session.state["ls"] = [x for x in args]
            if len(session.state["ls"]) == 0:
                session.finish("查询路由地址不能为空哦！")
            return
        if "-s" in args:
            args.remove("-s")

    if "mrfz" in args:
        session.state["ls"].append((getmrfz, "mrfz"))
        args.remove("mrfz")

    if "bcr" in args:
        session.state["ls"].append((getbcr, "bcr"))
        args.remove("bcr")

    if "gcores" in args:
        session.state["ls"].append((getgcores, "gcores"))
        args.remove("gcores")

    if "loli" in args:
        session.state["ls"].append((getloli, "loli"))
        args.remove("loli")

    if len(args) > 0:
        await session.send(
            unescape(
                "没有添加「{}」的订阅源！请联系".format(" ".join(args)) + cq.at(545870222) + "添加订阅！"
            )
        )
    if len(session.state["ls"]) == 0 and not session.is_first_run:
        session.finish("本次资讯查看为空哦！")


@on_command("ce", only_to_me=False, shell_like=True, permission=perm.SUPERUSER)
async def __(x):
    await bcr()
    await mrfz()
    await gcores()
    await loli()
