from nonebot import on_command, CommandSession, get_bot
from nonebot.command import call_command
from nonebot.message import escape as message_escape
import aiohttp
from nonebot.argparse import ArgumentParser

__plugin_name__ = "运行代码"

RUN_API_URL_FORMAT = "https://glot.io/run/{}?version=latest"
SUPPORTED_LANGUAGES = {
    "assembly": {"ext": "asm"},
    "bash": {"ext": "sh"},
    "c": {"ext": "c"},
    "clojure": {"ext": "clj"},
    "coffeescript": {"ext": "coffe"},
    "cpp": {"ext": "cpp"},
    "csharp": {"ext": "cs"},
    "erlang": {"ext": "erl"},
    "fsharp": {"ext": "fs"},
    "go": {"ext": "go"},
    "groovy": {"ext": "groovy"},
    "haskell": {"ext": "hs"},
    "java": {"ext": "java", "name": "Main"},
    "javascript": {"ext": "js"},
    "julia": {"ext": "jl"},
    "kotlin": {"ext": "kt"},
    "lua": {"ext": "lua"},
    "perl": {"ext": "pl"},
    "php": {"ext": "php"},
    "python": {"ext": "py"},
    "ruby": {"ext": "rb"},
    "rust": {"ext": "rs"},
    "scala": {"ext": "scala"},
    "swift": {"ext": "swift"},
    "typescript": {"ext": "ts"},
}

headers = {
    "Authorization": "Token {}".format(get_bot().config.RUNCODEAPI),
    "Content-type": "application/json",
}


@on_command("run", aliases=["运行代码", "运行"], only_to_me=False)
async def run(session: CommandSession):
    supported_languages = ", ".join(sorted(SUPPORTED_LANGUAGES.keys()))
    language = session.get(
        "language", prompt="你想运行的代码是什么语言？\n" f"目前支持 {supported_languages}"
    )
    code = session.get("code", prompt="你想运行的代码是？")
    await session.send("正在运行，请稍等……")
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.post(
            RUN_API_URL_FORMAT.format(language),
            json={
                "files": [
                    {
                        "name": (
                            SUPPORTED_LANGUAGES[language].get("name", "main")
                            + f'.{SUPPORTED_LANGUAGES[language]["ext"]}'
                        ),
                        "content": code,
                    }
                ],
                "stdin": "",
                "command": "",
            },
        ) as resp:

            if resp.status != 200:
                session.finish("运行失败，服务可能暂时不可用，请稍后再试")

            payload = await resp.json()
            if not isinstance(payload, dict):
                session.finish("运行失败，服务可能暂时不可用，请稍后再试")

    sent = False
    for k in ["stdout", "stderr", "error"]:
        v = payload.get(k)
        lines = v.splitlines()
        lines, remained_lines = lines[:10], lines[10:]
        out = "\n".join(lines)
        out, remained_out = out[: 60 * 10], out[60 * 10 :]

        if remained_lines or remained_out:
            out += f"\n（输出过多，已忽略剩余内容）"

        out = message_escape(out)
        if out:
            await session.send(f"{k}:\n\n{out}")
            sent = True

    if not sent:
        session.finish("运行成功，没有任何输出")


@on_command("cal", only_to_me=False)
async def cal(session: CommandSession):
    args = session.current_arg_text.strip()
    if args == "":
        session.finish("没有输入内容哦！")

    await call_command(
        session.bot, session.event, "run", current_arg="print({})".format(args)
    )


@run.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg == "":
            return
        parser = ArgumentParser(session=session)
        parser.add_argument("-l", "--language", default="python", help="指定编程语言")
        parser.add_argument("source", help="运行源代码", nargs="*")
        argv = parser.parse_args(stripped_arg.split(" "))
        language = argv.language
        if language not in SUPPORTED_LANGUAGES:
            session.finish("暂时不支持运行你输入的编程语言")
        session.state["language"] = language
        source = " ".join(argv.source)
        if source == "":
            return
        session.state["code"] = " ".join(argv.source)
        return

    if not stripped_arg:
        return

    if not stripped_arg:
        session.pause("请输入有效内容")
    if session.current_key == "language":
        if stripped_arg not in SUPPORTED_LANGUAGES:
            session.finish("暂时不支持运行你输入的编程语言")
    session.state[session.current_key] = stripped_arg
