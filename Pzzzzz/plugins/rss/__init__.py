from nonebot import on_command, CommandSession, on_startup
from nonebot.plugin import perm
from nonebot.command import Command, call_command
from nonebot.message import unescape, escape
import asyncio
import asyncpg
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from db import db
import cq
from utils import doc
import feedparser as fp
import re
from .utils import sendrss, getrss, handlerss, AutoReply
from .bcr import bcr
from .mrfz import mrfz
from .loli import loli
from .pork_price import pprice
from .bh3 import bh3
from .hpoi import hpoi
from .xlOfficial import xl
from .pixiv import pixiv
import time

__plugin_name__ = "rss 订阅"

NOUPDATE = ["loli", "hpoi"]
NOBROADCAST = ["gcores"]
FULLTEXT = ["pprice"]
BROADCASTGROUP = [
    145029700,
]


@nonebot.scheduler.scheduled_job("cron", hour="5", minute="0")
async def _():
    bot = nonebot.get_bot()
    async with db.pool.acquire() as conn:
        values = await conn.fetch("select gid from mg where morningcall = true")
        for item in values:
            item = item["gid"]
            try:
                await bot.send_group_msg(
                    group_id=int(item), message=f"Ciallo～(∠・ω< )⌒★，早上好。"
                )
            except CQHttpError:
                pass


@nonebot.scheduler.scheduled_job("cron", hour="0,6,12,18", minute="0")
async def bk():
    bot = nonebot.get_bot()
    async with db.pool.acquire() as conn:
        ls = await bot.get_group_member_list(
            group_id=bot.config.QGROUP, self_id=3418961367
        )
        await conn.execute("""delete from backup""")
        for item in ls:
            await conn.execute(
                f"""insert into backup values({item['user_id']},'{item['card']}','{item['role']}')"""
            )


@nonebot.scheduler.scheduled_job("interval", minutes=20)
async def __():
    bot = nonebot.get_bot()
    loop = asyncio.get_event_loop()
    async with db.pool.acquire() as conn:
        values = await conn.fetch("select gid from mg where rss = true")
        values = [int(item["gid"]) for item in values]
        for key in doc:
            if key in NOUPDATE or "pixiv" in key:
                continue
            asyncio.run_coroutine_threadsafe(
                handlerss(
                    bot,
                    key,
                    gtfun(key),
                    key not in NOBROADCAST,
                    key in FULLTEXT,
                    values,
                ),
                loop,
            )


@on_command("rss", only_to_me=False)
async def rss(session: CommandSession):
    if "subs" in session.state:
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
        for rt in session.state["ls"]:
            resp = await sendrss(
                session.event.user_id,
                session.bot,
                "自定义路由",
                None,
                getrss,
                (1, 1),
                route=rt,
            )
            if resp and session.event.detail_type != "private":
                await session.send(
                    unescape(cq.at(session.event.user_id) + f"「{rt}」的资讯已私信，请查收。")
                )

    elif "del" in session.state:
        async with db.pool.acquire() as conn:
            fail = []
            success = []
            for _, dl in session.state["ls"]:
                resp = await conn.execute(
                    "delete from subs where qid = {} and rss = '{}'".format(
                        session.event.user_id, dl
                    )
                )
                if resp[len("delete ") :] == "0":
                    fail.append(doc[dl])
                else:
                    success.append(doc[dl])
            if len(fail) > 0:
                await session.send(
                    cq.at(session.event.user_id)
                    + f"这{'个' if len(fail)==1 else '些'}源「{'、'.join(fail)}」不在你的订阅列表里面哦～"
                )
            if len(success) > 0:
                await session.send(
                    cq.at(session.event.user_id)
                    + f" 取消订阅「{'、'.join(success)}」成功！可喜可贺，可喜可贺！"
                )
    elif session.state["list"]:
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                "select * from subs where qid = {}".format(session.event.user_id)
            )
            if len(values) == 0:
                session.finish("貌似你没有订阅任何 rss 源")
            await session.send(
                cq.at(session.event.user_id)
                + "以下是你已订阅的源：\n{}".format(
                    "\n".join([doc[i["rss"]] + " - " + i["rss"] for i in values])
                )
            )

    else:
        loop = asyncio.get_event_loop()
        for item, nm in session.state["ls"]:
            asyncio.run_coroutine_threadsafe(
                sendrss(
                    session.event.user_id,
                    session.bot,
                    nm,
                    None,
                    item,
                    feedBack=session.event.group_id
                    if session.event.detail_type != "private"
                    else False,
                ),
                loop,
            )


@rss.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        parser = ArgumentParser(session=session)
        subparser = parser.add_mutually_exclusive_group()
        subparser.add_argument("-s", "--subs", nargs="+", help="订阅指定的 rss 源")
        subparser.add_argument("-r", "--route", nargs="+", help="获取自定路由的 rss 源的资讯")
        subparser.add_argument("-d", "--delete", nargs="+", help="删除 rss 订阅")
        subparser.add_argument(
            "-l", "--list", action="store_true", default=False, help="列出已订阅的源"
        )
        subparser.add_argument("-a", "--add", help="开通rss源")
        parser.add_argument("rss", nargs="*", help="获取已存在的 rss 源资讯")
        argv = parser.parse_args(session.current_arg_text.strip().split(" "))
        session.state["ls"] = []
        session.state["list"] = argv.list
        if argv.list:
            return
        if argv.subs != None:
            session.state["subs"] = argv.subs
            ls = argv.subs
        if argv.delete != None:
            session.state["del"] = argv.delete
            ls = argv.delete
        if argv.rss != []:
            session.state["rss"] = argv.rss
            ls = argv.rss
        if argv.route != None:
            session.state["route"] = argv.route
            session.state["ls"] = argv.route
            if len(session.state["ls"]) == 0:
                session.finish("查询路由地址不能为空哦！")
            return
        if argv.add != None:
            await session.send(str(session.event.user_id))
            result = await add_rss(argv.add.strip(), str(session.event.user_id))
            session.finish(result)

    ls = list(set(ls))
    if session.event.detail_type == "group":
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                "select safe from mg where gid = {}".format(session.event.group_id)
            )
            if len(values) > 0 and values[0]["safe"]:
                ls = [i for i in ls if "r18" not in i]

    for key in doc:
        if key in ls[:]:
            session.state["ls"].append((gtfun(key), key))
            ls.remove(key)

    if len(ls) > 0 and " ".join(ls).strip() != "":
        await session.send(
            unescape(
                "没有添加「{}」的订阅源！请联系".format(" ".join(ls)) + cq.at(545870222) + "添加订阅！"
            )
        )
    if len(session.state["ls"]) == 0:
        await session.send(
            "本次资讯{}为空哦！".format("查看" if session.state["rss"] != [] else "订阅")
        )
        session.finish(
            AutoReply(
                "Rss 指令帮助菜单",
                "以下是 rss 指令支持的源",
                [(i, j) for i, j in doc.items() if "r18" not in i],
            )
        )


@on_command("订阅", only_to_me=False, shell_like=True)
async def subs(session: CommandSession):
    ls = session.current_arg_text.strip(" ")

    flg = await call_command(
        session.bot,
        session.event,
        "rss",
        current_arg="-s " + ls,
        disable_interaction=True,
    )
    if flg == False:
        session.finish("订阅失败")


@on_command("取消订阅", only_to_me=False, shell_like=True)
async def unsubs(session: CommandSession):
    ls = session.current_arg_text.strip(" ")

    flg = await call_command(
        session.bot,
        session.event,
        "rss",
        current_arg="-d " + ls,
        disable_interaction=True,
    )
    if flg == False:
        session.finish("取消订阅失败")


@on_command("up", only_to_me=False, shell_like=True, permission=perm.SUPERUSER)
async def up(x):
    print(f"started at {time.strftime('%X')}")
    bot = nonebot.get_bot()
    loop = asyncio.get_event_loop()
    async with db.pool.acquire() as conn:
        values = await conn.fetch("select gid from mg where rss = true")
        values = [int(item["gid"]) for item in values]
        for key in doc:
            if key in NOUPDATE or "pixiv" in key:
                continue
            asyncio.run_coroutine_threadsafe(
                handlerss(
                    bot,
                    key,
                    gtfun(key),
                    key not in NOBROADCAST,
                    key in FULLTEXT,
                    values,
                ),
                loop,
            )
    print(f"finished at {time.strftime('%X')}")


@on_command("带礼包", only_to_me=False, shell_like=True, permission=perm.SUPERUSER)
async def _(session: CommandSession):
    event = {
        "user_id": session.event.user_id,
        "message": session.event.message,
        "post_type": "message",
        "message_type": "private",
        "raw_message": session.event.raw_message,
        "sub_type": "friend",
    }
    if session.event.detail_type != "private":
        event["message_type"] = "group"
        event["sub_type"] = None
        event["group_id"] = session.event.group_id
    await call_command(
        session.bot,
        session.event,
        "rss",
        current_arg="pixiv_day_r18 pixiv_week_r18 pixiv_day_male_r18",
    )


def gtfun(name: str):
    if "pixiv" in name:
        name = "pixiv"
    return getattr(sys.modules[__name__], name)
