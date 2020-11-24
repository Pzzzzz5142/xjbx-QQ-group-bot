from nonebot import on_notice, NoticeSession
import nonebot
from nonebot.command import call_command
from nonebot.message import unescape
import cq
import aiohttp
from utils import headers, getSetu


@on_notice("notify")
async def poke(session: NoticeSession):
    if session.event.sub_type == "poke" and session.event["target_id"] == 3418961367:
        x = await getSetu(False)
        await session.send(unescape(x))
        return

