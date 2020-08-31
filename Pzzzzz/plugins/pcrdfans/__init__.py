from nonebot import on_command, CommandSession

aliases = (
    "怎么拆",
    "怎么解",
    "怎么打",
    "如何拆",
    "如何解",
    "如何打",
    "怎麼拆",
    "怎麼解",
    "怎麼打",
    "jjc查询",
    "jjc查詢",
)


@on_command("b查询", aliases=aliases, only_to_me=False)
async def steal(session: CommandSession):
    await session.bot.send_group_msg(group_id=1044540742)
