from nonebot import on_command, CommandSession, permission as perm
from nonebot.message import unescape
import asyncio


@on_command("echo", only_to_me=False)
async def echo(session: CommandSession):
    a = await session.send(session.state.get("message") or session.current_arg)
    pass


@on_command("say", only_to_me=False, permission=perm.SUPERUSER)
async def say(session: CommandSession):
    await session.send(unescape(session.state.get("message") or session.current_arg))


@on_command("来一井", only_to_me=False, permission=perm.SUPERUSER)
async def say(session: CommandSession):
    for i in range(30):
        await session.send("抽卡")
        await asyncio.sleep(5)
