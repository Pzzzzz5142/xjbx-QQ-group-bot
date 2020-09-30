import json
from unittest.result import failfast
from aiocqhttp import event
from aiocqhttp.message import MessageSegment
from nonebot import on_command, CommandSession
from nonebot.message import unescape, escape
import nonebot
import aiohttp
from aiocqhttp.exceptions import Error as CQHttpError
from six import with_metaclass
from utils import *
import cq
from db import db
from random import randint
from utils import imageProxy, imageProxy_cat

__plugin_name__ = "以图搜图"

url = r"https://saucenao.com/search.php"

api = r"https://api.lolicon.app/setu/"

searchapi = r"https://api.imjad.cn/pixiv/v2/"

bot=nonebot.get_bot()

parm = {"apikey": bot.config.LoliAPI, "r18": "1", "size1200": "true"}
data = {"db": "999", "output_type": "2", "numres": "3", "url": None}
datas = {"sort": "腿控", "format": "images"}


@on_command("带礼包的怜悯", aliases=("怜悯"), only_to_me=False)
async def _(session: CommandSession):
    x = (
        "[CQ:json,data="
        + escape(
            '{"app":"com.tencent.autoreply","desc":"","view":"autoreply","ver":"0.0.0.1","prompt":"[可怜的人儿啊，请收下这份怜悯]","meta":{"metadata":{"title":"大礼包，向来不患寡而患不均","buttons":[{"slot":1,"action_data":"'
            + "rss pixiv_day_r18 pixiv_week_r18"
            + '","name":"点我领取带礼包的怜悯","action":"notify"}],"type":"guest","token":"LAcV49xqyE57S17B8ZT6FU7odBveNMYJzux288tBD3c="}},"config":{"forward":1,"showSender":1}}'
        )
        + "]"
    )
    await session.send(x)


@on_command("st", aliases={}, only_to_me=False)
async def st(session: CommandSession):

    purl = session.get("url", prompt="发送你想搜的图吧！")

    if "flg" not in session.state:
        session.state["flg"] = 1

    if "rl" in session.state:
        res, _id = await getRelated(
            session.state["id"], 0 if session.state["flg"] == 1 else -1
        )
        await session.send(res)
        if _id == -1:
            session.finish()
        session.state["id"] = _id
        session.state["flg"] = 0
        session.pause()

    if "r18" in session.state:
        res = cq.image(purl)
        if session.event.detail_type == "private":
            await session.send("拿到url了！正在发送图片！")
            await session.send(unescape(res))
            await session.send("图片发送完成，但是收不收得到就是缘分了！咕噜灵波～(∠・ω< )⌒★")
        else:
            try:
                bot = nonebot.get_bot()
                await bot.send_private_msg(
                    user_id=session.event.user_id, message="拿到url了！正在发送图片！",
                )
                await bot.send_private_msg(
                    user_id=session.event.user_id, message=res,
                )
                await bot.send_private_msg(
                    user_id=session.event.user_id,
                    message="图片发送完成，但是收不收得到就是缘分了！咕噜灵波～(∠・ω< )⌒★",
                )
            except CQHttpError:
                await session.send("网络错误哦！咕噜灵波～(∠・ω< )⌒★")
            session.finish("未找到消息中的图片，搜索结束！")
    elif "search" in session.state:
        safe = False
        if session.event.detail_type == "group":
            async with db.pool.acquire() as conn:
                values = await conn.fetch(
                    "select safe from mg where gid = {}".format(session.event.group_id)
                )
                safe = len(values) > 1 and values[0]["safe"]
        res, _id = await searchPic(session.state["search"], safe)
        await session.send(
            (
                cq.reply(session.event.message_id)
                if session.event.detail_type != "private"
                else ""
            )
            + res
        )
        session.state["id"] = _id
        if _id == -1:
            session.finish()
        session.pause()
    else:
        res = await sauce(purl)
        session.finish(unescape(res))


@st.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return

    if "flg" in session.state:
        if session.current_arg_text == "rl":
            session.state["rl"] = session.current_arg_text
        else:
            if session.state["flg"] == 1:
                session.switch(session.current_arg_text)
            session.finish("套娃结束！" if session.state["flg"] == 0 else None)

    if session.current_arg_text == "r16":
        async with aiohttp.ClientSession() as sess:
            async with sess.get("http://api.rosysun.cn/cos") as resp:
                if resp.status != 200:
                    return "网络错误哦，咕噜灵波～(∠・ω< )⌒★"
                ShitJson = await resp.text()
                await session.send(cq.image(ShitJson + ",cache=0"))
            async with sess.get(
                "https://api.uomg.com/api/rand.img3?sort=胖次猫&format=json"
            ) as resp:
                if resp.status != 200:
                    return "网络错误哦，咕噜灵波～(∠・ω< )⌒★"
                ShitData = await resp.read()
                ShitData = json.loads(ShitData)
                ShitData = ShitData["imgurl"]
                session.finish(cq.image(ShitData + ",cache=0"))

    if session.current_arg_text == "i":
        # await session.send("正在搜索图片！")
        async with aiohttp.ClientSession() as sess:
            async with sess.get(api, headers=headers, params=parm) as resp:
                if resp.status != 200:
                    session.finish("网络错误：" + str(resp.status))
                ShitJson = await resp.json()

        if ShitJson["quota"] == 0:
            session.finish(f"api调用额度已耗尽，距离下一次调用额度恢复还剩 {ShitJson['quota_min_ttl']} 秒。")
        session.state["url"] = ShitJson["data"][0]["url"]
        session.state["r18"] = 1
        # await session.send("届到了届到了！！！！")
        return

    elif len(session.current_arg_images) == 0:
        if session.current_arg_text.strip() != "":
            session.state["search"] = session.current_arg_text
        else:
            session.finish("嘛，什么都没输入嘛～～")
    else:
        session.state["url"] = session.current_arg_images[0]

@on_command('来份涩图',patterns="^来.*份.*(涩|色)图",only_to_me=False)
async def sst(session:CommandSession):
    msg=session.current_arg_text.strip()
    print(msg)
    if 'r18' in msg or 'R18' in msg:
        parm['r18']=1
    else:
        parm['r18']=0
    async with aiohttp.ClientSession() as sess:
        async with sess.get(api, headers=headers, params=parm) as resp:
            if resp.status != 200:
                session.finish("网络错误：" + str(resp.status))
            ShitJson = await resp.json()
    print(ShitJson)

    if ShitJson["quota"] == 0:
        session.finish(f"api调用额度已耗尽，距离下一次调用额度恢复还剩 {ShitJson['quota_min_ttl']} 秒。")
    session.finish(cq.image(ShitJson["data"][0]["url"]))


async def sauce(purl: str) -> str:

    data["url"] = purl

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=data, headers=headers) as resp:
            if resp.status != 200:
                return "错误：" + str(resp.status)
            ShitJson = await resp.json()

    if len(ShitJson["results"]) == 0:
        return "啥也没搜到"

    try:
        murl = hourse(ShitJson["results"][0]["data"]["ext_urls"][0])
    except:
        murl = ""

    return (
        cq.image(ShitJson["results"][0]["header"]["thumbnail"])
        + (
            f"\n标题：{ShitJson['results'][0]['data']['title']}"
            if "title" in ShitJson["results"][0]["data"]
            else ""
        )
        + (
            f"\nsource：{ShitJson['results'][0]['data']['source']}"
            if "source" in ShitJson["results"][0]["data"]
            else ""
        )
        + (
            f"\n日文名：{ShitJson['results'][0]['data']['jp_name']}"
            if "jp_name" in ShitJson["results"][0]["data"]
            else ""
        )
        + (
            f"\npixiv id: {ShitJson['results'][0]['data']['pixiv_id']}\n画师: {ShitJson['results'][0]['data']['member_name']}\n画师id: {ShitJson['results'][0]['data']['member_id']}"
            if "pixiv_id" in ShitJson["results"][0]["data"]
            else ""
        )
        + (f"\n来源（请复制到浏览器中打开，不要直接打开）：\n{murl}" if murl != "" else "")
        + "\n相似度："
        + str(ShitJson["results"][0]["header"]["similarity"])
        + "%"
    )


async def searchPic(key_word: str, safe=False):
    datas = {"type": "search", "word": key_word, "page": 1}
    async with aiohttp.ClientSession() as sess:
        async with sess.get(searchapi, params=datas) as resp:
            if resp.status != 200:
                return "网络错误哦，咕噜灵波～(∠・ω< )⌒★"
            ShitJson = await resp.json()
        ind = 10000000

        try:
            tt = ShitJson["illusts"]
            if safe:
                tt = [i for i in tt if "R-18" not in [j["name"] for j in i["tags"]]]
                print("safetilize")
            ind = randint(0, len(tt))
            res = cq.image(imageProxy(tt[ind]["image_urls"]["medium"]))
            ShitJson["illusts"] = tt

        except:
            res = f"暂时没有 {key_word} 的结果哦～"
        return (
            res,
            ShitJson["illusts"][ind]["id"] if ind < len(ShitJson["illusts"]) else res,
        )


async def getRelated(_id, ind=-1):
    datas = {"type": "related", "id": _id}
    async with aiohttp.ClientSession() as sess:
        async with sess.get(searchapi, params=datas) as resp:
            if resp.status != 200:
                return "网络错误哦，咕噜灵波～(∠・ω< )⌒★"
            ShitJson = await resp.json()
        if ind == -1 or ind >= len(ShitJson["illusts"]):
            ind = randint(0, len(ShitJson["illusts"]))
        try:
            res = cq.image(imageProxy(ShitJson["illusts"][ind]["image_urls"]["medium"]))
        except:
            res = f"暂时没有 {_id} 的相关结果哦～"
        return (
            res,
            ShitJson["illusts"][ind]["id"] if ind < len(ShitJson["illusts"]) else -1,
        )
