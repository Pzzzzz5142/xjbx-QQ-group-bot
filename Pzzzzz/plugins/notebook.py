from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db

NOTEUSAGE = r"""
备忘录命令！

使用方法：
 -a, --add X
            向备忘录中添加X
 -l, --list 
            查看备忘录中的物品
 -d, --del X
            删除备忘录中的物品
 -c, --cls
            清空备忘录

例如：
    使用
        note -a 茄子
    来记录物品 茄子 。
""".strip()

__plugin_name__ = '备忘录'
__plugin_usage__ = NOTEUSAGE


@on_command('notebook', aliases={'note', '备忘', '备忘录'}, only_to_me=False, shell_like=True)
async def notebook(session: CommandSession):

    if session.is_first_run:
        parser = ArgumentParser(session=session, usage=NOTEUSAGE)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-a', '--add', type=str, help="添加物品")
        group.add_argument('-l', '--list', action='store_true', help="查看物品")
        group.add_argument('-d', '--delt', type=str, help="删除物品")
        group.add_argument('-c', '--cls', action='store_true', help="清空物品")

        args = parser.parse_args(session.argv)
    else:
        stripped_arg = session.current_arg_text.strip()

    if not session.is_first_run and(not stripped_arg and stripped_arg != '是' and stripped_arg != '否'):
        session.pause('要输入「是」或者「否」中的一个哦。')

    if session.is_first_run and args.add != None:
        if len(args.add) > 20:
            session.finish('呀，物品名称长度不能超过 20 哦～')
        try:
            state = await db.conn.execute('''insert into notebook (qid,item) values ({0},'{1}');'''.format(session.event.sender['user_id'], args.add))
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            await db.conn.execute('''insert into quser (qid,swid) values ({0},{1});'''.format(session.event.sender['user_id'], swFormatter(session.event.sender['card'] if session.event['message_type'] != 'private' else '-1')))
            state = await db.conn.execute('''insert into notebook (qid,item) values ({0},'{1}');'''.format(session.event.sender['user_id'], args.add))
        except asyncpg.exceptions.UniqueViolationError as e:
            session.finish('你已经添加过该物品啦！')
        session.finish('物品：{0} 添加完毕！'.format(args.add))

    elif session.is_first_run and args.list == True:
        values = await db.conn.fetch('''select * from notebook where qid={0} order by item;'''.format(session.event.sender['user_id']))
        if len(values) == 0:
            session.finish('并没有找到任何记录，蛮遗憾的。')
        log = "\n"
        for index, item in enumerate(values):
            if index % 10 == 0 and index != 0:
                await session.send(log[2:])
                log = "\n"
            log += "\n{0}. {1}".format(index + 1, item['item'])
        await session.send(log[2:])
        session.finish('以上')

    elif 'del' in session.state or (session.is_first_run and args.delt != None):
        if session.is_first_run:
            state = await db.conn.execute('''select * from notebook where qid={0} and item = '{1}';'''.format(session.event.sender['user_id'], args.delt))
            if int(state[6:]) == 0:
                session.finish('貌似，并没有找到该记录？你输入的记录为 {0}'.format(args.delt))
            session.state['del'] = args.delt
            session.pause('确定要删除吗？（请输入「是」或「否」）')
        if stripped_arg == '是':
            state = await db.conn.execute('''delete from notebook where qid={0} and item = '{1}';'''.format(session.event.sender['user_id'], session.state['del']))
            session.finish('确认删除惹！')
        else:
            session.finish('删除撤销！')

    elif 'cls' in session.state or (session.is_first_run and args.cls == True) == True:
        if session.is_first_run:
            session.state['cls'] = 1
            session.pause('确定要清空所有记录吗？（请输入「是」或「否」）')
        if stripped_arg == '是':
            state = await db.conn.execute('''delete from notebook where qid={0};'''.format(session.event.sender['user_id']))
            session.finish('完 全 清 空 ！')
        else:
            session.finish('删除撤销！')

    else:
        session.finish('啥玩意没有，建议重来。')
