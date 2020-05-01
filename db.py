import asyncio
import asyncpg
import os
import yaml
from nonebot import on_startup, get_bot
from nonebot.log import logger


class A(object):
    conn = None
    pool = None

    async def setBind(self):
        bot = get_bot()
        try:
            self.pool = await asyncpg.create_pool(dsn=bot.config.DATABASE)
        except:
            logger.warning("数据库配置失败，某些功能可能不可用")


db = A()


async def initdb():
    await db.setBind()


async def create_schema():
    await db.setBind()
    try:
        async with db.pool.acquire() as conn:
            await conn.execute(
                """create table jrrp(
                qid bigint primary key,
                dt date,
                rand int
            )"""
            )
            await conn.execute(
                """create table rss(
                id varchar(20) primary key,
                dt varchar(50),
            )"""
            )
            await conn.execute(
                """create table subs(
                qid bigint,
                dt varchar(50),
                rss varchar(20) references rss (id) on update cascade on delete cascade
                primary key (qid,rss)
            )"""
            )
            await conn.execute("""create index on subs(rss)""")
    except:
        logger.error("操作失败，可能是数据库配置不正确！")
        exit(1)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(create_schema())
