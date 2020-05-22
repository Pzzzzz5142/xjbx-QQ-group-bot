from nonebot import on_command, CommandSession, on_startup, permission as perm
from nonebot.command import call_command
from nonebot.message import unescape
import asyncio
import asyncpg
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
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
from .pork_price import pprice, getpprice
from .bh3 import bh3, getbh3
from .hpoi import hpoi, gethpoi

__plugin_name__ = "rss 订阅"


@nonebot.scheduler.scheduled_job("cron", hour="5", minute="0")
async def _():
    bot = nonebot.get_bot()
    try:
        await bot.send_group_msg(
            group_id=bot.config.QGROUP, message=f"Ciallo～(∠・ω< )⌒★，早上好。"
        )
    except CQHttpError:
        pass


@nonebot.scheduler.scheduled_job("interval", minutes=20)
# @on_command("ce", only_to_me=False, shell_like=True)
async def __():
    await bcr()
    await mrfz()
    await gcores()
    # await loli()
    await pprice()
    await bh3()


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
                            session.event.user_id, "No Information", item
                        )
                    )
                    await session.send(f"「{doc[item]}」的资讯已添加订阅了！有新资讯发布时，会私信你哦！")
                except asyncpg.exceptions.ForeignKeyViolationError:
                    await session.send(f"貌似系统并没有支持该订阅源的订阅！")
                    logger.error("no", exc_info=True)
                except asyncpg.exceptions.UniqueViolationError:
                    await session.send(f"你已经添加过「{doc[item]}」的资讯订阅啦！")
                except:
                    await session.send(
                        f"发生未知错误！错误详细信息已记录了在log中！\n定位 message id 为：{session.event.message_id}"
                    )
                    logger.error("some rss issue", exc_info=True)

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
        bot = nonebot.get_bot()
        for item, nm in session.state["ls"]:
            resp = await sendrss(session.event.user_id, bot, nm, None, item, (1, 1))
            if resp and session.event.detail_type != "private":
                await session.send(
                    unescape(cq.at(session.event.user_id) + f"「{doc[nm]}」的资讯已私信，请查收。")
                )


@rss.args_parser
async def _(session: CommandSession):
    arg = session.current_arg_text.strip()
    args = arg.split(" ")
    args = [i for i in args if i != ""]

    if session.is_first_run:
        parser=ArgumentParser(session=session)
        subparser=parser.add_mutually_exclusive_group()
        subparser.add_argument('-s','--subs',help='订阅指定的 rss 源')
        subparser.add_argument('-r','--route',help='获取指定 rss 源的资讯')
        subparser.add_argument('-d','--delete',help='删除 rss 订阅')
        parser.add_argument('ls',help='要处理的 rss 列表',nargs='+')
        argv=parser.parse_args(args)
        session.state["ls"] = []
        session.state["subs"] = 1 if (len(argv.ls) > 0 and argv.subs) else 0
        if argv.route != None:
            session.state["route"] = "ok"
            session.state["ls"] = [x for x in argv.ls]
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

    if "pprice" in args:
        session.state["ls"].append((getpprice, "pprice"))
        args.remove("pprice")

    if "bh3" in args:
        session.state["ls"].append((getbh3, "bh3"))
        args.remove("bh3")

    if "hpoi" in args:
        session.state["ls"].append((gethpoi, "hpoi"))
        args.remove("hpoi")

    if len(args) > 0:
        await session.send(
            unescape(
                "没有添加「{}」的订阅源！请联系".format(" ".join(args)) + cq.at(545870222) + "添加订阅！"
            )
        )
    if len(session.state["ls"]) == 0 and (not session.is_first_run or arg != ""):
        session.finish(
            "本次资讯{}为空哦！".format("查看" if session.state["subs"] == 0 else "订阅")
        )


@on_command("订阅", only_to_me=False, shell_like=True)
async def subs(session: CommandSession):
    args = session.current_arg_text.strip(" ")

    flg = await call_command(
        session.bot,
        session.event,
        "rss",
        current_arg="-s " + args,
        disable_interaction=True,
    )
    if flg == False:
        session.finish("订阅失败")


@on_command("up", only_to_me=False, shell_like=True, permission=perm.SUPERUSER)
async def up(x):
    await bcr()
    await mrfz()
    await gcores()
    await hpoi()
    await pprice()
    await bh3()
