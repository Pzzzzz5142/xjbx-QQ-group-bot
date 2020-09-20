from nonebot import on_command, CommandSession
from nonebot.command import call_command
import asyncio


@on_command("debug", only_to_me=False)
async def debug(session: CommandSession):
    x = session.get("x", prompt="这是x")
    x = session.get("y", prompt="这是y")
    x = session.get("z", prompt="这是z")

    if x == "ok":
        x = await call_command(session.bot, session.event, "debug1")
        await session.send("蛤蛤蛤蛤")
        x = session.get("j", prompt="这是乱入")
        # await session.pause("123")
    await session.send("finished")


@debug.args_parser
async def _(session: CommandSession):
    await session.send("IN ARGS PARSER")
    session.state[session.current_key] = session.current_arg_text.strip()
    await session.send(str(session.state))


@on_command("debug1", only_to_me=False)
async def debug1(session: CommandSession):
    x = session.get("x", prompt="这是x 1")
    x = session.get("y", prompt="这是y 1")
    x = session.get("z", prompt="这是z 1")


@debug1.args_parser
async def _(session: CommandSession):
    await session.send("IN ARGS PARSER 1")
    session.state[session.current_key] = session.current_arg_text.strip()
    await session.send(str(session.state))


@on_command("debug2", only_to_me=False)
async def debug2(session: CommandSession):
    x = session.get("x", prompt="这是x")
    x = session.get("y", prompt="这是y")
    x = session.get("z", prompt="这是z")


@debug2.args_parser
async def _(session: CommandSession):
    await session.send("IN ARGS PARSER 2")
    session.state[session.current_key] = session.current_arg_text.strip()
