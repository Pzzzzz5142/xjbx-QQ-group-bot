from os import posix_fadvise
from nonebot import NoneBot
from nonebot import session
from nonebot.message import message_preprocessor, CanceledException
from nonebot.plugin import on_command, CommandSession, PluginManager, perm
from aiocqhttp.exceptions import Error as CQHttpError
from db import db
import aiocqhttp

cmd = {
    "safe": "安全模式",
    "rss": "群内 rss 通知",
    "white": "是否相应本群消息",
    "ghz": "公会战模式",
    "morningcall": "早安！",
}


@on_command("on", only_to_me=False, permission=perm.SUPERUSER)
async def on(session: CommandSession):
    await swcmd(session, True)


@on_command("off", only_to_me=False, permission=perm.SUPERUSER)
async def on(session: CommandSession):
    await swcmd(session, False)


@on_command("mg", only_to_me=False, permission=perm.SUPERUSER)
async def mg(session: CommandSession):
    session.finish("{}")


@on_command("grant", only_to_me=False, permission=perm.SUPERUSER)
async def mg(session: CommandSession):
    a = session.current_arg_text.strip().split()
    async with db.pool.acquire() as conn:
        for i in a:
            await conn.execute(
                "insert into mg (gid,white) values ({},{})".format(int(i), True)
            )

    await session.send("已给群「{}」基础版授权。".format(" 、".join(a)))


@message_preprocessor
async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
    if event.detail_type != "group":
        print(event.detail_type)
        return
    async with db.pool.acquire() as conn:
        values = await conn.fetch(
            "select * from mg where gid = {}".format(event.group_id)
        )
        if "on" == event.raw_message[:2] or "off" == event.raw_message[:3]:
            return
        if len(values) == 0:
            raise CanceledException("该群不处于白名单中")


async def swcmd(session: CommandSession, on: bool):
    if session.event.detail_type == "private":
        session.finish("目前仅支持针对群聊的操控哦！")
    ccmd = session.current_arg_text.strip().split(" ")
    ans = []
    async with db.pool.acquire() as conn:
        values = await conn.fetch(
            """select * from mg where gid={}""".format(session.event.group_id)
        )
        if len(values) == 0:
            await conn.execute(
                "insert into mg (gid,white) values ({},{})".format(
                    session.event.group_id, on
                )
            )
        for i in ccmd:
            if i in cmd:
                await conn.execute(
                    """update mg set {} = {} where gid = {}""".format(
                        i, on, session.event.group_id
                    )
                )
                ans.append(cmd[i])
    if len(ans) > 0:
        session.finish("{} 功能已{}".format("、".join(ans), "开启" if on else "关闭"))

