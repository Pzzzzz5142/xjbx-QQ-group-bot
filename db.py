import asyncio
import asyncpg
import os
import yaml
from nonebot import on_startup


class A(object):
    conn = None

    async def setBind(self, kwarg):
        try:
            self.conn = await asyncpg.connect(user=kwarg['user'], password=kwarg['password'],
                                              database=kwarg['database'], host=kwarg['host'])
        except:
            raise Exception('数据库配置出错惹，请检查数据库配置文件 config.yml！')


db = A()


async def initdb():
    global conn
    conn = 1
    filePath = os.path.join(os.path.dirname(__file__), 'config.yml')
    fl = open(filePath, 'r', encoding='utf-8')
    config = yaml.load(fl)

    await db.setBind(config)

    fl.close()

    return
