from nonebot import CommandSession, on_command
from nonebot.message import unescape
import cq


@on_command("卡池完善", only_to_me=False)
async def ckcp(session: CommandSession):
    await session.send("这是明日方舟的卡池完善表哦！")
    await session.send(
        unescape(
            cq.link(
                "https://oitncsu-my.sharepoint.com/:x:/g/personal/yzhan268_ncsu_edu/EW_cNFDzEH1PoNZCBosO7CYBK-micmOICkuKHayogDt7Lg?e=bPdaMB",
                "明日方舟",
                "卡池完善表格",
            )
        )
    )
