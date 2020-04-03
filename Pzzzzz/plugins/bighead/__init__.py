from nonebot import on_command, CommandSession,on_startup
from nonebot.message import unescape
import asyncio
import asyncpg
from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError

@on_startup
async def 

@nonebot.scheduler.scheduled_job('cron', hour='12', day_of_week='0-6')
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    try:
        await bot.send_group_msg(group_id=851733906,
                                 message=f'现在{now.hour}点整啦！大头菜价格刷新了！')
    except CQHttpError:
        pass

