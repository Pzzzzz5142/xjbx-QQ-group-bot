from nonebot import on_command, CommandSession
from nonebot.command import call_command


@on_command("debug", only_to_me=False)
async def debug(session: CommandSession):
    x = session.get("x", prompt="这是x")
    x = session.get("y", prompt="这是y")
    x = session.get("z", prompt="这是z")

    if x == "ok":
        await call_command(session.bot, session.event, "debug")


@debug.args_parser
async def _(session: CommandSession):
    await session.send("IN ARGS PARSER")
    session.state[session.current_key] = session.current_arg_text.strip()
