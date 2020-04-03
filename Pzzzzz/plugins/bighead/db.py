import asyncio
import asyncpg
import os
import yaml
from nonebot import on_startup

@on_startup
async def initdb():
    global conn
    filePath = os.path.join(os.path.dirname(__file__), 'config.yml')
    fl = open(filePath, 'r', encoding='utf-8')
    config = yaml.load(fl)

    try:
        conn = await asyncpg.connect(user=config['user'], password=config['password'],
                                     database=config['database'], host=config['host'])
    except:
        raise Exception('数据库配置出错惹，请检查数据库配置文件 config.yml！')

    return