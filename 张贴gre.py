import asyncio
import asyncpg

async def run():
    conn = await asyncpg.connect(user='postgres', password='hello123aaa',
                                 database='postgres', host='127.0.0.1')
    try:
        values = await conn.execute('''insert into datouroom (qid,price) values ('545870222',123);''')
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        print('ok')
    print(values)
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())