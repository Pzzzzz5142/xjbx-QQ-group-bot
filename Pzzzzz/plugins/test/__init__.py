from nonebot import on_command, CommandSession
from nonebot.message import unescape


@on_command('try', only_to_me=False)
async def test(session: CommandSession):
    await session.send('Enter send')
    if len(session.event.sender) == 0:
        await session.send('Nothing to send!')
    else:
        await session.send(len(session.event.sender))
    for key, value in session.event.sender.items():
        await session.send('{0},{1}'.format(key, value))
    await session.send(unescape('[CQ:at,qq=%d] Finish! session.state len = %d' % (session.event.sender['user_id'], len(session.state))))
