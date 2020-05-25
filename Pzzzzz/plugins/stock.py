from nonebot import CommandSession, on_command
from nonebot.argparse import ArgumentParser
import yfinance as yf
import aiohttp
import pandas as pd
from db import db
from nonebot.command import call_command
import aiocqhttp
import cq

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
        try:
            currency = ShitJson["currency"]
        except:
            session.finish(
                "获取股票信息失败，请检查股票代码是否输入正确！\n当前输入为「{}」".format(session.state["q"])
            )
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
            try:
                await conn.execute(
                    f"insert into acc (qid) values ({session.event.user_id})"
                )
                await session.send("注册成功！当前注册资本为 1000000 美元。")
            except:
                session.finish("你已经注册过了！")

    if session.state["h"]:
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                f"select money from acc where qid={session.event.user_id}"
            )
            if len(values) == 0:
                session.finish("您尚未注册", ensure_private=True)
            money = values[0]["money"]
            values = await conn.fetch(
                f"select * from holds where qid={session.event.user_id}"
            )
            values = [(i["stk"], i["nums"]) for i in values if i["nums"] > 0]
            if len(values) == 0:
                session.finish("当前您未持股哦！", ensure_private=True)

            if session.event.detail_type != "private":
                await session.send(
                    cq.at(session.event.user_id) + " 资产统计信息正在发送中，咕噜灵波～ (∠・ω< )⌒★"
                )

            await session.send("正在统计您的资产。。。", ensure_private=True)
            res = []
            fail = []
            cnt = 0
            tot = 0
            async with aiohttp.ClientSession() as sess:
                for item, nums in values:
                    async with sess.get(qurl + item, params=qdatas) as resp:
                        app = ""
                        if resp.status != 200:
                            fail.append(item)
                        else:
                            ShitJson = await resp.json()
                            ShitJson = ShitJson["quoteSummary"]["result"][0]["price"]
                            price = float(ShitJson["regularMarketPrice"]["fmt"]) * nums
                            tot += price
                            app = f"\n价值：{price} USD"
                    if cnt < 5:
                        res.append(f"股票代码：{item}\n持股数：{nums} 股" + app)
                    cnt += 1
            await session.send("以下是您持有的股份：", ensure_private=True)
            for msg in res:
                await session.send(msg, ensure_private=True)
            await session.send(
                f"共持股：{len(values)} 支\n共计：{tot+money} USD。现金额度为：{money} USD。"
                + (f"其中 「{', '.join(fail)}」 股票价格获取失败。" if len(fail) > 0 else ""),
                ensure_private=True,
            )
            if session.event.detail_type != "private":
                await session.send(
                    cq.at(session.event.user_id)
                    + f" 共持股：{len(values)} 支\n共计：{tot+money} USD。现金额度为：{money} USD。"
                    + (f"其中 「{', '.join(fail)}」 股票价格获取失败。" if len(fail) > 0 else ""),
                )

    if "add" in session.state:
        if session.event.detail_type == "private":
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
                                ShitJson = ShitJson["quoteSummary"]["result"][0][
                                    "price"
                                ]
                                price = float(ShitJson["regularMarketPrice"]["fmt"])
                                if isinstance(session.state["nums"], int):
                                    if money < session.state["nums"] * price:
                                        fail.append((item, "余额不足"))
                                    else:
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
                                    nums = int(money / price)
                                    tot += price * nums
                                    if nums == 0:
                                        fail.append((item, f"当前余额不足以购买一支「{item}」股票"))
                                    else:
                                        success.append(
                                            (item, price, nums, price * nums)
                                        )
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
                await session.send(f"交易前余额：「{money}」USD。交易后余额：「{money-tot}」USD。")
                if len(success) == 0:
                    session.finish("无可交易操作，交易终止。")
            confirm = session.get("confirm", prompt="请确认这笔交易！输入「确认」进行确认，输入其他任意值取消这笔交易。")
            if confirm == "确认":
                success, fail = session.state["trade"]
                async with db.pool.acquire() as conn:
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
            else:
                session.finish("交易取消")
        else:
            event = {
                "user_id": session.event.user_id,
                "message": session.event.message,
                "raw_message": session.event.raw_message,
                "post_type": "message",
                "message_type": "private",
                "sub_type": "friend",
            }
            await session.send(cq.at(session.event.user_id) + " 转进私聊中。。。")
            flg = await call_command(
                session.bot,
                aiocqhttp.Event(event),
                "stock",
                current_arg=session.current_arg,
            )
            if not flg:
                await session.send("转进失败，请尝试直接复制以下信息并发送以完成操作。", ensure_private=True)
                await session.send("stk " + session.current_arg, ensure_private=True)

    if "sell" in session.state:
        if session.event.detail_type == "private":
            if session.is_first_run:
                ls = session.state["sell"]
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
                    if len(ls) == 0:
                        values = await conn.fetch(
                            "select * from holds where qid = {}".format(
                                session.event.user_id
                            )
                        )
                        ls = [i["stk"] for i in values if i["nums"] != 0]
                        if len(ls) == 0:
                            session.finish("您尚未有购买股票记录")
                    async with aiohttp.ClientSession() as sess:
                        for item in ls:
                            values = await conn.fetch(
                                "select nums from holds where qid={1} and stk ='{0}'".format(
                                    item, session.event.user_id
                                )
                            )
                            if len(values) == 0:
                                fail.append((item, "您未购买该股票"))
                                continue
                            nums = values[0]["nums"]
                            async with sess.get(qurl + item, params=qdatas) as resp:
                                app = ""
                                if resp.status != 200:
                                    fail.append((item, "无法获取最新股票价格"))
                                else:
                                    ShitJson = await resp.json()
                                    ShitJson = ShitJson["quoteSummary"]["result"][0][
                                        "price"
                                    ]
                                    price = float(ShitJson["regularMarketPrice"]["fmt"])
                                    if isinstance(session.state["nums"], int):
                                        if nums < session.state["nums"]:
                                            fail.append(item, "出售支数大于拥有支数")
                                        else:
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
                                        tot += price * nums
                                        success.append(
                                            (item, price, nums, price * nums)
                                        )
                session.state["trade"] = (success, fail)
                await session.send("以下是本次交易信息：")
                if len(success) > 0:
                    await session.send("可以完成的操作：")
                    for i in success:
                        await session.send(
                            "股票代码：{}\n股票单价：{}\n出售支数：{}\n合计金额：{}".format(
                                i[0], i[1], i[2], i[3]
                            )
                        )
                if len(fail) > 0:
                    await session.send("无法完成的操作：")
                    for i in fail:
                        await session.send("股票代码：{}\n原因：{}".format(i[0], i[1]))
                await session.send(f"交易前余额：「{money}」USD。交易后余额：「{money+tot}」USD。")
                if len(success) == 0:
                    session.finish("无可交易操作，交易终止。")
            confirm = session.get("confirm", prompt="请确认这笔交易！输入「确认」进行确认，输入其他任意值取消这笔交易。")
            if confirm == "确认":
                success, fail = session.state["trade"]
                async with db.pool.acquire() as conn:
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
                                    "update holds set nums = nums - {2} where qid = {0} and stk = '{1}'".format(
                                        session.event.user_id, item[0], item[2]
                                    )
                                )
                            await conn.execute(
                                f"update acc set money = money + {item[3]} where qid={session.event.user_id};"
                            )
                await session.send("交易完成！")
            else:
                session.finish("交易取消")
        else:
            event = {
                "user_id": session.event.user_id,
                "message": session.event.message,
                "post_type": "message",
                "message_type": "private",
                "raw_message": session.event.raw_message,
                "sub_type": "friend",
            }
            await session.send(cq.at(session.event.user_id) + " 转进私聊中。。。")
            flg = await call_command(
                session.bot,
                aiocqhttp.Event(event),
                "stock",
                current_arg=session.current_arg,
            )
            if not flg:
                await session.send("转进失败，请尝试直接复制以下信息并发送以完成操作。", ensure_private=True)
                await session.send("stk " + session.current_arg, ensure_private=True)


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
            "--signup", "-i", action="store_true", default=False, help="注册"
        )
        parser.add_argument(
            "--list", "-l", action="store_true", default=False, help="查看持股"
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
            "--allin", "-a", action="store_true", default=False, help="allout"
        )
        sell.add_argument("ssymbol", help="抛售的股票编号。", nargs="*")

        argv = parser.parse_args(arg.split(" "))

        session.state["s"] = argv.url if argv.url != None else argv.show
        session.state["q"] = argv.query
        session.state["i"] = argv.signup
        session.state["h"] = argv.list
        try:
            session.state["add"] = [i.lower() for i in argv.symbol]
        except:
            pass
        try:
            session.state["sell"] = [i.lower() for i in argv.ssymbol]
        except:
            pass
        try:
            session.state["nums"] = "allin" if argv.allin else argv.nums
        except:
            pass
    else:
        session.state["confirm"] = session.current_arg.strip()


@on_command("买进", only_to_me=False)
async def buy(session: CommandSession):
    if session.is_first_run:
        session.state["buy"] = session.current_arg_text.strip().lower()
        if session.state["buy"] == "":
            session.finish("买进不能为空哦！")
        session.pause("请问你要买几支呢？")

    try:
        nums = int(session.current_arg_text)
        arg = f"buy -n {nums} "
    except:
        if session.current_arg_text in ("allin", "all", "全部"):
            arg = "buy -a "
        else:
            session.finish("请输入阿拉伯数字！")

    session.switch("stk " + arg + session.state["buy"])


@on_command("卖出", aliases={"抛售"}, only_to_me=False)
async def buy(session: CommandSession):
    if session.is_first_run:
        session.state["sell"] = session.current_arg_text.strip().lower()
        if session.state["sell"] == "":
            session.finish("出售不能为空哦！")
        session.pause("请问你要卖几支呢？")

    try:
        nums = int(session.current_arg_text)
        arg = f"sell -n {nums} "
    except:
        if session.current_arg_text in ("allin", "all", "全部"):
            arg = "sell -a "
        else:
            session.finish("请输入阿拉伯数字！")

    session.switch("stk " + arg + session.state["sell"])
