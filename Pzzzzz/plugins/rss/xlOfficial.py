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
from utils import *
from .utils import sendrss, rssBili
import feedparser as fp
import re


async def xl(max_num: int = -1):
    return await rssBili(49458759, max_num)

