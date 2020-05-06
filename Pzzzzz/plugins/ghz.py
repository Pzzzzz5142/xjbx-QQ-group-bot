from nonebot.message import unescape
import asyncio
import asyncpg
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import cq
from nonebot import on_command, CommandSession
from utils import *
import feedparser as fp
import re
import aiohttp


@on_command("出刀")
async def cd(session: CommandSession):
    pass
