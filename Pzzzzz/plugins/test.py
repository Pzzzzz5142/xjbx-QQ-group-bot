from nonebot import on_command, CommandSession, on_startup, permission as perm
from nonebot.message import unescape
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
from nonebot.log import logger
import cq


@on_command("test", shell_like=True, only_to_me=False, permission=perm.SUPERUSER)
async def test(session: CommandSession):
    bot = nonebot.get_bot()
    parser = ArgumentParser(session=session)
    parser.add_argument("-e", "--end", action="store_true", help="解除禁言")

    args = parser.parse_args(session.argv)

    if args.end:
        try:
            await bot.set_group_ban(
                group_id=bot.config.QGROUP, user_id=3313437849, duration=0
            )
            await session.send(unescape("解除禁言" + cq.at(3313437849) + "成功"))
        except CQHttpError:
            await session.send(unescape("解除禁言" + cq.at(3313437849) + "失败"))

        try:
            await bot.set_group_ban(
                group_id=bot.config.QGROUP, user_id=2682823919, duration=0
            )
            await session.send(unescape("解除禁言" + cq.at(2682823919) + "成功"))
        except CQHttpError:
            await session.send(unescape("解除禁言" + cq.at(2682823919) + "失败"))

    else:
        try:
            await bot.set_group_ban(group_id=bot.config.QGROUP, user_id=3313437849)
            await session.send(unescape("禁言" + cq.at(3313437849) + "成功"))
        except CQHttpError:
            await session.send(unescape("禁言" + cq.at(3313437849) + "失败"))

        try:
            await bot.set_group_ban(group_id=bot.config.QGROUP, user_id=2682823919)
            await session.send(unescape("禁言" + cq.at(2682823919) + "成功"))
        except CQHttpError:
            await session.send(unescape("禁言" + cq.at(2682823919) + "失败"))
