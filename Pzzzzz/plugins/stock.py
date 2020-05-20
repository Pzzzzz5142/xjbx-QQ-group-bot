from nonebot import CommandSession, on_command
from nonebot.argparse import ArgumentParser
import yfinance as yf
import aiohttp
import pandas as pd
from db import db

qurl = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
qdatas = {"modules": "price"}


@on_command("stock", aliases={"stk"}, only_to_me=False)
async def stock(session: CommandSession):
    if session.state["s"]:
        await session.send("正在获取股票信息")
        surl = (
            "https://finance.yahoo.com/screener/predefined/most_actives?count=10&offset=0"
            if isinstance(session.state["s"], bool)
            else session.state["s"]
        )
        async with aiohttp.ClientSession() as sess:
            async with sess.get(surl) as resp:
                if resp.status != 200:
                    session.finish(f"获取股票失败，请检查url是否正确！错误代码：{resp.status}")
                ShitHtml = await resp.text()
        data = pd.read_html(ShitHtml)[0]

        stk_list = data.values

        await session.send("以下是股票查询结果：")
        stk = ""
        cnt = 0
        for i in stk_list:
            if cnt == 10:
                break
            cnt += 1
            stk += (
                f"股票代码：{i[0]}，价格：{i[2]}，变动幅度：{i[4]} "
                + ("↓" if i[4][0] == "-" else "↑")
                + "\n\n"
            )
        stk += "以上！"
        await session.send(stk)

    if session.state["q"] != None:
        await session.send("正在查询 " + session.state["q"] + "！")
        async with aiohttp.ClientSession() as sess:
            async with sess.get(qurl + session.state["q"], params=qdatas) as resp:
                if resp.status != 200:
                    session.finish(
                        "获取股票信息失败，请检查股票代码是否输入正确！\n当前输入为「{}」".format(session.state["q"])
                    )
                ShitJson = await resp.json()

        ShitJson = ShitJson["quoteSummary"]["result"][0]["price"]
        currency = ShitJson["currency"]
        res = (
            f"公司名：{ShitJson['shortName']}\n"
            + "当前货币单位为："
            + currency
            + f"\n当前股票价格为：{ShitJson['regularMarketPrice']['fmt']}"
        )
        res += f"\n当日最高成交价格为：{ShitJson['regularMarketDayHigh']['fmt']}\n当日最低成交价格为：{ShitJson['regularMarketDayLow']['fmt']}\n变动幅度为：{ShitJson['regularMarketChangePercent']['fmt']}"

        await session.send(res)

    if session.state["i"]:
        async with db.pool.acquire() as conn:
            await conn.execute(
                f"insert into acc (qid) values ({session.event.user_id})"
            )
            await session.send("注册成功！当前注册资本为 10000000000 美元。")

    if session.state["h"]:
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                f"select * from holds where qid={session.event.user_id}"
            )
            if len(values) == 0:
                session.finish("当前您未持股哦！")
            await session.send("正在统计您的资产。。。")
            res = []
            fail = []
            cnt = 0
            tot = 0
            async with aiohttp.ClientSession() as sess:
                for item in values:
                    async with sess.get(url + item["stk"], params=qdatas):
                        app = ""
                        if resp.status != 200:
                            fail.append(item["stk"])
                        else:
                            ShitJson = await resp.json()
                            price = (
                                int(ShitJson["regularMarketPrice"]["fmt"])
                                * item["nums"]
                            )
                            tot += price
                            app = f"\n价值：{price} USD"
                    if cnt < 5:
                        res.append(f"股票代码：{item['stk']}\n持股数：{item['nums']} 股" + app)
                    cnt += 1
            session.send("以下是您持有的股份：\n")
            for msg in res:
                await session.send(msg)
            await session.send(f'共计：{tot} USD。其中 「{", ".join(fail)}」 股票价格获取失败。')


@stock.args_parser
async def _(session: CommandSession):
    arg = session.current_arg_text.strip()

    if session.is_first_run:
        parser = ArgumentParser(session=session)

        parser.add_argument(
            "--show",
            "-s",
            action="store_true",
            default=False,
            help="列出前10个 Most Actives 股票清单",
        )
        parser.add_argument("--url", "-u", type=str, help="想查询的 Yahoo 链接")
        parser.add_argument("--query", "-q", type=str, help="查询指定股票信息")
        parser.add_argument(
            "--signin", "-i", action="store_true", default=False, help="注册"
        )
        parser.add_argument(
            "--holds", "-H", action="store_true", default=False, help="查看持股"
        )
        argv = parser.parse_args(arg.split(" "))

        session.state["s"] = argv.url if argv.url != None else argv.show
        session.state["q"] = argv.query
        session.state["i"] = argv.signin
        session.state["h"] = argv.holds
