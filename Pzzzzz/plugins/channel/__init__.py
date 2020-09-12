from nonebot import on_command, CommandSession, get_bot
from nonebot.command import call_command
from nonebot.message import escape as message_escape
import aiohttp
from nonebot.argparse import ArgumentParser


@on_command("channel",only_to_me=False)
async def channel(session:CommandSession):
    if session.event.detail_type!='private':
        session.finish("channel命令仅适用于私聊使用")

    content=session.get('content',prompt='要发布的内容')
    


@channel.args_parser
async def _(session:CommandSession):
    pass