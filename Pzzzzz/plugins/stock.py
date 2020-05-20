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
                                float(ShitJson["regularMarketPrice"]["fmt"])
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

    if session.state["add"] != None:
        if session.is_first_run:
            ls = session.state["add"]
            fail = []
            success = []
            tot = 0
            async with db.pool.acquire() as conn:
                values = await conn.fetch(
                    f"select money from acc where qid={session.event.user_id}"
                )
                if len(values) == 0:
                    session.finish("您尚未注册！")
                money = values[0]["money"]
            await session.send("test")
            async with aiohttp.ClientSession() as sess:
                if len(ls) > 1 and session.state["nums"] == "allin":
                    session.finish("多种股票不支持 allin 操作！")
                for item in ls:
                    async with sess.get(qurl + item, params=qdatas) as resp:
                        app = ""
                        if resp.status != 200:
                            fail.append((item, "无法获取最新股票价格"))
                        else:
                            ShitJson = await resp.json()
                            ShitJson = ShitJson["quoteSummary"]["result"][0]["price"]
                            price = float(ShitJson["regularMarketPrice"]["fmt"])
                            if isinstance(session.state["nums"], int):
                                if money < session.state["nums"] * price:
                                    fail.append(item, "余额不足")
                                else:
                                    success.append(item, session.state["nums"])
                                    money -= session.state["nums"] * price
                                    tot += session.state["nums"] * price
                                    success.append(
                                        (
                                            item,
                                            price,
                                            session.state["nums"],
                                            price * session.state["nums"],
                                        )
                                    )
                            else:
                                nums = money // price
                                tot += money - price * nums
                                money -= price * nums
                                if nums == 0:
                                    fail.append(item, f"当前余额不足以购买一支「{item}」股票")
                                else:
                                    success.append((item, price, nums, price * nums))
            session.state["trade"] = (success, fail)
            await session.send("以下是本次交易信息：")
            if len(success) > 0:
                await session.send("可以完成的操作：")
                for i in success:
                    await session.send(
                        "股票代码：{}\n股票单价：{}\n购买支数：{}\n合计金额：{}".format(
                            i[0], i[1], i[2], i[3]
                        )
                    )
            if len(fail) > 0:
                await session.send("无法完成的操作：")
                for i in fail:
                    await session.send("股票代码：{}\n原因：{}".format(i[0], i[1]))
            await session.send(f"交易前余额：「{money+tot}」USD。交易后余额：「{money}」USD。")
        confirm = session.get("confirm", prompt="请确认这笔交易！输入「确认」进行确认，输入其他任意值取消这笔交易。")
        if confirm == "确认":
            success, fail = session.state["trade"]
            async with db.pool.acquire() as conn:
                money = await conn.fetch(
                    f"select money from acc where qid={session.event.user_id}"
                )
                money = money[0]["money"]
                for item in success:
                    async with conn.transaction():
                        values = await conn.fetch(
                            "select * from holds where qid={} and stk='{}'".format(
                                session.event.user_id, item[0]
                            )
                        )
                        if len(values) == 0:
                            await conn.execute(
                                "insert into holds values({},'{}',{})".format(
                                    session.event.user_id, item[0], item[2]
                                )
                            )
                        else:
                            await conn.execute(
                                "update holds set nums = nums + {2} where qid = {0} and stk = '{1}'".format(
                                    session.event.user_id, item[0], item[2]
                                )
                            )
                        await conn.execute(
                            f"update acc set money = money - {item[3]} where qid={session.event.user_id};"
                        )
            await session.send("交易完成！")
            
    if session.state["add"] != None:
        if session.is_first_run:
            ls = session.state["add"]
            fail = []
            success = []
            tot = 0
            async with db.pool.acquire() as conn:
                values = await conn.fetch(
                    f"select money from acc where qid={session.event.user_id}"
                )
                if len(values) == 0:
                    session.finish("您尚未注册！")
                money = values[0]["money"]
            await session.send("test")
            async with aiohttp.ClientSession() as sess:
                if len(ls) > 1 and session.state["nums"] == "allin":
                    session.finish("多种股票不支持 allin 操作！")
                for item in ls:
                    async with sess.get(qurl + item, params=qdatas) as resp:
                        app = ""
                        if resp.status != 200:
                            fail.append((item, "无法获取最新股票价格"))
                        else:
                            ShitJson = await resp.json()
                            ShitJson = ShitJson["quoteSummary"]["result"][0]["price"]
                            price = float(ShitJson["regularMarketPrice"]["fmt"])
                            if isinstance(session.state["nums"], int):
                                if money < session.state["nums"] * price:
                                    fail.append(item, "余额不足")
                                else:
                                    success.append(item, session.state["nums"])
                                    money -= session.state["nums"] * price
                                    tot += session.state["nums"] * price
                                    success.append(
                                        (
                                            item,
                                            price,
                                            session.state["nums"],
                                            price * session.state["nums"],
                                        )
                                    )
                            else:
                                nums = money // price
                                tot += money - price * nums
                                money -= price * nums
                                if nums == 0:
                                    fail.append(item, f"当前余额不足以购买一支「{item}」股票")
                                else:
                                    success.append((item, price, nums, price * nums))
            session.state["trade"] = (success, fail)
            await session.send("以下是本次交易信息：")
            if len(success) > 0:
                await session.send("可以完成的操作：")
                for i in success:
                    await session.send(
                        "股票代码：{}\n股票单价：{}\n购买支数：{}\n合计金额：{}".format(
                            i[0], i[1], i[2], i[3]
                        )
                    )
            if len(fail) > 0:
                await session.send("无法完成的操作：")
                for i in fail:
                    await session.send("股票代码：{}\n原因：{}".format(i[0], i[1]))
            await session.send(f"交易前余额：「{money+tot}」USD。交易后余额：「{money}」USD。")
        confirm = session.get("confirm", prompt="请确认这笔交易！输入「确认」进行确认，输入其他任意值取消这笔交易。")
        if confirm == "确认":
            success, fail = session.state["trade"]
            async with db.pool.acquire() as conn:
                money = await conn.fetch(
                    f"select money from acc where qid={session.event.user_id}"
                )
                money = money[0]["money"]
                for item in success:
                    async with conn.transaction():
                        values = await conn.fetch(
                            "select * from holds where qid={} and stk='{}'".format(
                                session.event.user_id, item[0]
                            )
                        )
                        if len(values) == 0:
                            await conn.execute(
                                "insert into holds values({},'{}',{})".format(
                                    session.event.user_id, item[0], item[2]
                                )
                            )
                        else:
                            await conn.execute(
                                "update holds set nums = nums + {2} where qid = {0} and stk = '{1}'".format(
                                    session.event.user_id, item[0], item[2]
                                )
                            )
                        await conn.execute(
                            f"update acc set money = money - {item[3]} where qid={session.event.user_id};"
                        )
            await session.send("交易完成！")


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
        sub = parser.add_subparsers()

        add = sub.add_parser("buy", help="买进股票")

        subadd = add.add_mutually_exclusive_group()
        subadd.add_argument("--nums", "-n", type=int, help="购入数量")
        subadd.add_argument(
            "--allin", "-a", action="store_true", default=False, help="allin"
        )
        add.add_argument("symbol", help="买进的股票编号。", nargs="+")

        sell = sub.add_parser("sell", help="抛售股票")

        subsell = sell.add_mutually_exclusive_group()
        subsell.add_argument("--nums", "-n", type=int, help="抛售数量")
        subsell.add_argument(
            "--allin", "-a", action="store_true", default=False, help="allin"
        )
        sell.add_argument("symbol", help="抛售的股票编号。", nargs="+")

        argv = parser.parse_args(arg.split(" "))

        session.state["s"] = argv.url if argv.url != None else argv.show
        session.state["q"] = argv.query
        session.state["i"] = argv.signin
        session.state["h"] = argv.holds
        session.state["add"] = argv.symbol
        session.state["nums"] = "allin" if argv.allin else argv.holds
    else:
        session.state["confirm"] = session.current_arg.strip()
