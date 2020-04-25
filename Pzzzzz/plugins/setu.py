from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime
import nonebot
import asyncio
import asyncpg
from aiocqhttp.exceptions import Error as CQHttpError
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
from utils import * 

url = r"https://saucenao.com/search.php"

@on_command('setu', aliases={}, only_to_me=False, shell_like=True)
async def setu(session: CommandSession):
    pass