from nonebot import on_command, CommandSession, on_startup
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

random.seed(114514)

roomset = []

BIGUSAGE = r"""
大头菜挂牌上市命令！

使用方法：
 -p, --price X
            以X的价格发布你岛上的大头菜

例如：
    使用 
        大头菜 -p 650 
        或者 
        大头菜 --price 650
    来让你的大头菜以650的价格挂牌上市！

注意！
    1）当大头菜价格刷新时，你的大头菜价格将会被强制下市。
    2）如果你输错了，直接重新输入命令来更新大头菜价格！
""".strip()


def isdigit(c: str) -> bool:
    try:
        c = int(c)
    except:
        return False
    return True


def swFormatter(thing: str):
    pre = None
    sw = ""

    for i in range(len(thing)):
        if isdigit(thing[i]):
            sw += thing[i]
        elif thing[i] not in [' ', '-']:
            sw = ""

    if sw == "" or len(sw) != 12:
        sw = '-1'

    return sw


@nonebot.scheduler.scheduled_job('cron', hour='12,0', day_of_week='0-6', minute='*')
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    try:
        await db.conn.execute('''delete from datouroom''')
        await bot.send_group_msg(group_id=851733906,
                                 message=f'现在{now.hour}点整啦！大头菜价格刷新了！')
    except CQHttpError:
        pass


@on_command('大头菜', only_to_me=False, shell_like=True)
async def bighead(session: CommandSession):

    global roomset

    parser = ArgumentParser(session=session, usage=BIGUSAGE)
    parser.add_argument('-p', '--price', type=int,
                        help="大头菜的价格", required=True)

    args = parser.parse_args(session.argv)
    roomnum = randint(0, 1000000)
    while roomnum in roomset:
        roomnum = randint(0, 1000000)
    bisect.insort(roomset, roomnum)

    try:
        state = await db.conn.execute('''insert into datouroom (qid,price,roomnum) values ({0},{1},{2});'''.format(session.event.sender['user_id'], args.price, roomnum))
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        await db.conn.execute('''insert into quser (qid,swid) values ({0},{1});'''.format(session.event.sender['user_id'], swFormatter(session.event.sender['card'] if session.event['message_type'] != 'private' else '-1')))
        state = await db.conn.execute('''insert into datouroom (qid,price,roomnum) values ({0},{1},{2});'''.format(session.event.sender['user_id'], args.price, roomnum))
    except asyncpg.exceptions.UniqueViolationError as e:
        state = await db.conn.execute('''update datouroom set price = {1} where qid='{0}';'''.format(session.event.sender['user_id'], args.price))

    values = await db.conn.fetch('''select * from datouroom where qid = {0}'''.format(session.event.sender['user_id']))

    logger.info('操作完成')

    session.finish(
        '''已{2}如下记录：
    QQ号：{0}
    大头菜价格：{1}
    房间号：{3}'''.format(values[0]['qid'], values[0]['price'], '添加' if 'UPDATE' not in state else '更新', values[0]['roomnum']))
