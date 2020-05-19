from nonebot import CommandSession, on_command
from nonebot.argparse import ArgumentParser
import yfinance as yf
import aiohttp
import pandas as pd


@on_command("stock", aliases={"stk"}, only_to_me=False)
async def stock(session: CommandSession):
    if session.state["s"]:
        await session.send("正在获取股票信息")
        url = (
            "https://finance.yahoo.com/screener/predefined/most_actives?count=10&offset=0"
            if isinstance(session.state["s"], bool)
            else session.state["s"]
        )
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                if resp.status != 200:
                    session.finish(f"获取股票失败，请检查url是否正确！错误代码：{resp.status}")
                ShitHtml = await resp.text()
        data = pd.read_html(ShitHtml)[0]

        stk_list = data.Symbol

        await session.send("以下是股票查询结果：")
        stk = ""
        cnt = 0
        for i in stk_list:
            if cnt == 10:
                break
            cnt += 1
            stk += i + "\n"
        stk += "以上！"
        await session.send(stk)


@stock.args_parser
async def _(session: CommandSession):
    arg = session.current_arg_text.strip()

    if session.is_first_run:
        parser = ArgumentParser(session=session)

        parser.add_argument(
            "--show", "-s", action="store_true", help="列出前10个 Most Actives 股票清单"
        )
        parser.add_argument("--url", "-u", type=str, help="想查询的 Yahoo 链接")
        argv = parser.parse_args(arg.split(" "))

        session.state["s"] = argv.url if argv.url != None else argv.show
