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
""".strip()


@on_startup
async def initdb():
    global conn
    filePath = os.path.join(os.path.dirname(__file__), 'config.yml')
    fl = open(filePath, 'r', encoding='utf-8')
    config = yaml.load(fl)

    try:
        conn = await asyncpg.connect(user=config['user'], password=config['password'],
                                     database=config['database'], host=config['host'])
    except:
        raise Exception('数据库配置出错惹，请检查数据库配置文件 config.yml！')

    return


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
    global conn
    try:
        await conn.execute('''delete from datouroom''')
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
        state = await conn.execute('''insert into datouroom (qid,price,roomnum) values ({0},{1},{2});'''.format(session.event.sender['user_id'], args.price, roomnum))
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        await conn.execute('''insert into quser (qid,swid) values ({0},{1});'''.format(session.event.sender['user_id'], swFormatter(session.event.sender['card'] if session.event['message_type'] != 'private' else '-1')))
        state = await conn.execute('''insert into datouroom (qid,price,roomnum) values ({0},{1},{2});'''.format(session.event.sender['user_id'], args.price, roomnum))
    except asyncpg.exceptions.UniqueViolationError as e:
        state = await conn.execute('''update datouroom set price = {1} where qid='{0}';'''.format(session.event.sender['user_id'], args.price))

    values = await conn.fetch('''select * from datouroom where qid = {0}'''.format(session.event.sender['user_id']))

    session.finish(
        '''已{2}如下记录：
    QQ号：{0}
    大头菜价格：{1}
    房间号：{3}'''.format(values[0]['qid'], values[0]['price'], '添加' if 'UPDATE' not in state else '更新', values[0]['roomnum']))
    logger.info('操作完成')


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
            state = await conn.execute('''insert into notebook (qid,item) values ({0},'{1}');'''.format(session.event.sender['user_id'], args.add))
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            await conn.execute('''insert into quser (qid,swid) values ({0},{1});'''.format(session.event.sender['user_id'], swFormatter(session.event.sender['card'] if session.event['message_type'] != 'private' else '-1')))
            state = await conn.execute('''insert into notebook (qid,item) values ({0},'{1}');'''.format(session.event.sender['user_id'], args.add))
        except asyncpg.exceptions.UniqueViolationError as e:
            session.finish('你已经添加过该物品啦！')
        session.finish('物品：{0} 添加完毕！'.format(args.add))

    elif session.is_first_run and args.list == True:
        values = await conn.fetch('''select * from notebook where qid={0} order by item;'''.format(session.event.sender['user_id']))
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

    elif 'del' in session.state or args.delt != None:
        if session.is_first_run:
            state = await conn.execute('''select * from notebook where qid={0} and item = '{1}';'''.format(session.event.sender['user_id'], args.delt))
            if int(state[6:]) == 0:
                session.finish('貌似，并没有找到该记录？你输入的记录为 {0}'.format(args.delt))
            session.state['del'] = args.delt
            session.pause('确定要删除吗？（请输入「是」或「否」）')
        if stripped_arg == '是':
            state = await conn.execute('''delete from notebook where qid={0} and item = '{1}';'''.format(session.event.sender['user_id'], session.state['del']))
            session.finish('确认删除惹！')
        else:
            session.finish('删除撤销！')

    elif 'cls' in session.state or args.cls == True:
        if session.is_first_run:
            session.state['cls'] = 1
            session.pause('确定要清空所有记录吗？（请输入「是」或「否」）')
        if stripped_arg == '是':
            state = await conn.execute('''delete from notebook where qid={0};'''.format(session.event.sender['user_id']))
            session.finish('完 全 清 空 ！')
        else:
            session.finish('删除撤销！')

    else:
        session.finish('啥玩意没有，建议重来。')
