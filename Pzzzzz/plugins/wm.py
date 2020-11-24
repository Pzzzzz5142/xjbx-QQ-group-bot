from nonebot import CommandSession, on_command
from langdetect import detect, detect_langs
from aiohttp import ClientSession
from nonebot import get_bot
from nonebot.argparse import ArgumentParser
import time
import hmac
import random, sys
import hashlib
import binascii
import urllib

bot = get_bot()
# 百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# coding=utf-8

import hashlib
import urllib
import random


@on_command("wm", aliases={"翻译", "translate"}, only_to_me=False)
async def wm(session: CommandSession):
    session.get("token", prompt="请输入你想翻译的句子！")
    myurl = "/api/trans/vip/translate"
    q = session.state["token"]
    fromLang = session.state["fr"]  # 原文语种
    toLang = session.state["to"]  # 译文语种
    salt = random.randint(32768, 65536)
    sign = bot.config.BAIDUAPI + q + str(salt) + bot.config.BAIDUKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = (
        myurl
        + "?appid="
        + bot.config.BAIDUAPI
        + "&q="
        + urllib.parse.quote(q)
        + "&from="
        + fromLang
        + "&to="
        + toLang
        + "&salt="
        + str(salt)
        + "&sign="
        + sign
    )
    async with ClientSession() as sess:
        async with sess.get("https://fanyi-api.baidu.com" + myurl) as resp:
            if resp.status != 200:
                pass
            ShitAns = await resp.json()
    try:
        ans = [i["dst"] for i in ShitAns["trans_result"]]
        ans = "\n".join(ans)
    except:
        session.finish("翻译错误，原因是：" + ShitAns["error_code"])

    session.finish("翻译结果为：\n" + ans)


@wm.args_parser
async def _(session: CommandSession):
    arg = session.current_arg_text.strip()

    if session.is_first_run:
        parser = ArgumentParser(session=session)

        parser.add_argument("--fr", "-f", type=str, default="no")
        parser.add_argument("--to", "-t", type=str, default="no")
        parser.add_argument("token", type=str, default="", nargs="+")
        argv = parser.parse_args(session.current_arg.split(" "))

        arg = " ".join(argv.token)

    if arg == "":
        session.pause("输入不能为空哦！")

    session.state["fr"] = detect(arg) if argv.fr == "no" else argv.fr

    if session.state["fr"][:2] == "zh":
        session.state["fr"] = "zh"

    if argv.to == "no":
        if session.state["fr"] == "zh":
            session.state["to"] = "en"
        else:
            session.state["to"] = "zh"
    else:
        session.state["to"] = argv.to

    if argv.fr == "no":
        session.state["fr"] = "auto"

    session.state["token"] = arg
