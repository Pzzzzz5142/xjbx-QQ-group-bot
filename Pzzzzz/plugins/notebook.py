from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime
import nonebot
import asyncio
import asyncpg
from aiocqhttp.exceptions import Error as CQHttpError
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
from utils import *

NOTEUSAGE = r"""
备忘录命令！

命令：'note' 或 'notebook' 或 '备忘' 或 '备忘录'

功能参数：
 -a, --add X
            向备忘录中添加X
 -l, --list 
            查看备忘录中的记录
            
 -d, --del X
            删除备忘录中的记录
            开头为「*」则被解释为序号
            如 note -d *1 则会删除第「1」条记录
 -c, --cls
            清空备忘录

例如：
    使用
        note -a 茄子
    来记录记录 茄子 。
""".strip()

# __plugin_name__ = '备忘录'
# __plugin_usage__ = NOTEUSAGE


@on_command(
    "notebook", aliases={"note", "备忘", "备忘录"}, only_to_me=False, shell_like=True
)
async def notebook(session: CommandSession):

    if session.is_first_run:
        parser = ArgumentParser(session=session, usage=NOTEUSAGE)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", "--add", type=str, nargs="+", help="添加记录")
        group.add_argument("-l", "--list", action="store_true", help="查看记录")
        group.add_argument("-d", "--delt", type=str, help="删除记录")
        group.add_argument("-c", "--cls", action="store_true", help="清空记录")
        group.add_argument("-ls", "--listsort", action="store_true")

        args = parser.parse_args(session.argv)
    else:
        stripped_arg = session.current_arg_text.strip()

    if not session.is_first_run and (
        not stripped_arg and stripped_arg != "是" and stripped_arg != "否"
    ):
        session.pause("要输入「是」或者「否」中的一个哦。")

    if session.is_first_run and args.add != None:
        args.add = " ".join(args.add)
        if len(args.add) > 50:
            session.finish("呀，记录的长度不能超过 50 哦～")
        if args.add[0] == "*":
            session.finish("哦，当前并不支持以「*」开头的记录哦～")
        async with db.pool.acquire() as conn:
            try:
                values = await conn.fetch(
                    f"""select noteind from quser where qid = {session.event.user_id};"""
                )
                ind = values[0]["noteind"]
            except IndexError:
                await conn.execute(
                    """insert into quser (qid,swid) values ({0},{1});""".format(
                        session.event.user_id,
                        swFormatter(
                            session.event.sender["card"]
                            if session.event["message_type"] != "private"
                            else "-1"
                        ),
                    )
                )
                values = await conn.fetch(
                    f"""select noteind from quser where qid = {session.event.user_id};"""
                )
                ind = values[0]["noteind"]

            try:
                state = await conn.execute(
                    """insert into notebook (qid,item,ind) values ({0},'{1}',{2});""".format(
                        session.event.user_id, args.add, ind
                    )
                )
            except asyncpg.exceptions.ForeignKeyViolationError as e:
                await conn.execute(
                    """insert into quser (qid,swid) values ({0},{1});""".format(
                        session.event.user_id,
                        swFormatter(
                            session.event.sender["card"]
                            if session.event["message_type"] != "private"
                            else "-1"
                        ),
                    )
                )
                state = await conn.execute(
                    """insert into notebook (qid,item,ind) values ({0},'{1}',{2});""".format(
                        session.event.user_id, args.add, ind
                    )
                )
            except asyncpg.exceptions.UniqueViolationError as e:
                session.finish("你已经添加过该记录啦！")
            await conn.execute(
                f"""update quser set noteind = {ind + 1} where qid={session.event.user_id}"""
            )
            session.finish("记录：{0} 添加完毕！".format(args.add))

    elif session.is_first_run and args.list == True:
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                """select * from notebook where qid={0} order by ind;""".format(
                    session.event.user_id
                )
            )
        if len(values) == 0:
            session.finish("并没有找到任何记录，蛮遗憾的。")
        log = "\n"
        for item in values:
            if item["ind"] % 10 == 0 and item["ind"] != 0:
                await session.send(log[2:])
                log = "\n"
            log += "\n{0}. {1}".format(item["ind"] + 1, item["item"])
        await session.send(log[2:])
        session.finish("以上")

    elif session.is_first_run and args.listsort == True:
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                """select * from notebook where qid={0} order by item;""".format(
                    session.event.user_id
                )
            )
        if len(values) == 0:
            session.finish("并没有找到任何记录，蛮遗憾的。")
        log = "\n"
        for item in values:
            if item["ind"] % 10 == 0 and item["ind"] != 0:
                await session.send(log[2:])
                log = "\n"
            log += "\n{0}. {1}".format(item["ind"] + 1, item["item"])
        await session.send(log[2:])
        session.finish("以上")

    elif "del" in session.state or (session.is_first_run and args.delt != None):
        async with db.pool.acquire() as conn:
            if session.is_first_run:
                flg = 0
                if args.delt[0] == "*":
                    try:
                        args.delt = int(args.delt[1:]) - 1
                        flg = 1
                    except:
                        session.finish("「*」开头的记录表示记录序列号哦。")
                    values = await conn.fetch(
                        """select * from notebook where qid={0} and ind = '{1}';""".format(
                            session.event.user_id, args.delt
                        )
                    )
                else:
                    values = await conn.fetch(
                        """select * from notebook where qid={0} and item = '{1}';""".format(
                            session.event.user_id, args.delt
                        )
                    )
                if len(values) == 0:
                    session.finish(
                        "貌似，并没有找到该记录？你输入的记录为 {0}".format(
                            args.delt if flg == 0 else f"序列号：{args.delt + 1}"
                        )
                    )
                item = values[0]["item"]
                session.state["del"] = item
                session.state["delind"] = values[0]["ind"]
                session.pause(f"确定要删除「{item}」吗？（请输入「是」或「否」）")
            if stripped_arg == "是":
                state = await conn.execute(
                    """delete from notebook where qid={0} and item = '{1}';
                update notebook set ind = ind - 1 where ind > {2} and qid={0};
                update quser set noteind = noteind - 1 where qid = {0};""".format(
                        session.event.user_id,
                        session.state["del"],
                        session.state["delind"],
                    )
                )
                session.finish("确认删除「{}」了！".format(session.state["del"]))
            else:
                session.finish("删除撤销！")

    elif "cls" in session.state or (session.is_first_run and args.cls == True) == True:
        if session.is_first_run:
            session.state["cls"] = 1
            session.pause("确定要清空所有记录吗？（请输入「是」或「否」）")
        if stripped_arg == "是":
            async with db.pool.acquire() as conn:
                state = await conn.execute(
                    """delete from notebook where qid={0};
                update quser set noteind = 0 where qid = {0};""".format(
                        session.event.user_id
                    )
                )
                session.finish("完 全 清 空 ！")
        else:
            session.finish("删除撤销！")
