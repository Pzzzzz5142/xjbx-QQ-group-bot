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
import cq
from utils import *

random.seed(114514)

BIGUSAGE = r"""
大头菜命令！

命令：'大头菜'

功能参数：
 -p, --price X
            以X的价格发布你岛上的大头菜
 -l, --list
            查看当前所有大头菜价格
 -d, --delt
            删除你自己的房间

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

maxbig_head = 0

__plugin_name__ = '大头菜挂牌上市'
__plugin_usage__ = BIGUSAGE

def roomPaser(value, lv: int = 0) -> str:
    return '\t'*lv + f"QQ号：{value['qid']}\n"+'\t'*lv+f"大头菜价格：{value['price']}"


@nonebot.scheduler.scheduled_job('cron', hour='12,22', day_of_week='0-6', minute='0')
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    try:
        await db.conn.execute('''delete from datou''')
        await bot.send_group_msg(group_id=1093759055,
                                 message=f'现在{now.hour}点整啦！大头菜价格刷新了！')
    except CQHttpError:
        pass


@on_command('大头菜', only_to_me=False, shell_like=True)
async def bighead(session: CommandSession):

    parser = ArgumentParser(session=session, usage=BIGUSAGE)
    group = parser.add_argument_group()
    group.add_argument('-p', '--price', type=int, help="大头菜的价格")
    group.add_argument('-l', '--list', action='store_true',
                       help="列出当前有的大头菜价格", default=False)
    group.add_argument('-d', '--delt', action='store_true',
                       help='删除你自己的大头菜价格', default=False)

    args = parser.parse_args(session.argv)
    if args.price != None:
        if args.price > 810 or args.price < 0:
            session.finish('小老弟，你怎么回事？')

        try:
            state = await db.conn.execute('''insert into datou (qid,price) values ({0},{1});'''.format(session.event.user_id, args.price))
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            await db.conn.execute('''insert into quser (qid,swid) values ({0},{1});'''.format(session.event.user_id, swFormatter(session.event.sender['card'] if session.event['message_type'] != 'private' else '-1')))
            state = await db.conn.execute('''insert into datou (qid,price) values ({0},{1});'''.format(session.event.user_id, args.price))
        except asyncpg.exceptions.UniqueViolationError as e:
            state = await db.conn.execute('''update datou set price = {1} where qid='{0}';'''.format(session.event.user_id, args.price))

        values = await db.conn.fetch('''select * from datou where qid = {0}'''.format(session.event.user_id))

        logger.info('大头菜上市完成')

        session.finish(
            '已{}如下记录：\n'.format('添加' if 'UPDATE' not in state else '更新') + roomPaser(values[0], 1))

    elif args.list == True:
        bot = nonebot.get_bot()
        values = await db.conn.fetch('''select * from datou order by price DESC''')
        if len(values) == 0:
            session.finish('很遗憾，当前没有大头菜报价。')
        for i in range(min(maxbig_head, len(values))):
            await session.send(roomPaser(values[i]))
        if session.event['message_type'] == 'group'and len(values) <= maxbig_head:
            await session.send(unescape(f"{cq.at(session.event.user_id)} 全部报价如上。"))
        try:
            for value in values[maxbig_head:]:
                await bot.send_private_msg(message=roomPaser(value), user_id=session.event.user_id)
            if len(values) > maxbig_head:
                await bot.send_private_msg(message='全部报价如上。', user_id=session.event.user_id)
        except CQHttpError:
            session.finish(unescape(f'{cq.at(session.event.user_id)} 剩余大头菜报价信息发送失败，请尝试与我发送临时消息。'))
        if len(values) > maxbig_head and session.event['message_type'] == 'group':
            pass
            # await session.send(unescape(f'{cq.at(session.event.user_id)} 剩余大头菜报价已私发，请查收。'))

    elif args.delt == True:
        value = await db.conn.execute(f'select * from datou where qid={session.event.user_id}')
        if len(value) == 0:
            session.finish('你貌似并没有上市的大头菜。')
        await db.conn.execute(f'''delete from datou where qid={session.event.user_id};''')
        session.finish('删除完成')
