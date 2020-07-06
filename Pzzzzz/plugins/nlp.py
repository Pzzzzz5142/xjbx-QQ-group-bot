from nonebot import on_natural_language, NLPSession
import re
from random import random
from .repeat import repeat
from .qieqie_cp import decherulize


@on_natural_language(only_to_me=False, only_short_message=False)
async def _(session: NLPSession):
    if re.match("切噜～♪", session.msg_text) != None:
        await decherulize(session)
    await repeat(session)
