import json

import base64
from re import S
from nonebot import on_command, CommandSession
from nonebot.message import unescape, escape
import nonebot
import aiohttp
from aiocqhttp.exceptions import Error as CQHttpError
from utils import *
import cq
import random
from utils import imageProxy, imageProxy_cat, cksafe

__plugin_name__ = "以图搜图"

url = r"https://saucenao.com/search.php"
pixivicurl = "https://api.pixivic.com/"

api = r"https://api.lolicon.app/setu/"

searchapi = r"https://api.imjad.cn/pixiv/v2/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
    "Authorization": "eyJhbGciOiJIUzUxMiJ9.eyJwZXJtaXNzaW9uTGV2ZWwiOjEsInJlZnJlc2hDb3VudCI6MSwiaXNCYW4iOjEsInVzZXJJZCI6NTkyMDA4LCJpYXQiOjE2MDU4NzIzMzEsImV4cCI6MTYwNjA0NTEzMX0.h8EzXhflPXxQcIBS8nTm8E8mL-SStmsybmsYM24hdBFCKIEsZfYzuzdsfgB7GJWsB2GGuoZCCaBRT1l7Amjp4Q",
    "Referer": "https://pixivic.com/",
}

bot = nonebot.get_bot()

parm = {"apikey": bot.config.LoliAPI, "r18": "1", "size1200": "true"}
data = {"db": "999", "output_type": "2", "numres": "3", "url": None}
datas = {"sort": "腿控", "format": "images"}


@on_command("login", only_to_me=False)
async def login(session: CommandSession):
    parm = {"username": bot.config.USERNAME, "password": bot.config.PASSWORD}

    if session.is_first_run:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(pixivicurl + "verificationCode") as resp:
                if resp.status != 200:
                    session.finish("获取验证码失败")
                ShitJson = await resp.json()
                img = ShitJson["data"]["imageBase64"]
                vid = ShitJson["data"]["vid"]
                session.state["imageBase64"] = img
                session.state["vid"] = vid
                session.get("img", prompt=cq.image("base64://" + img))
    q = {"vid": session.state["vid"], "value": session.state["img"]}
    async with aiohttp.ClientSession() as sess:
        async with sess.post(pixivicurl + "users/token", params=q, json=parm) as resp:
            if resp.status != 200:
                session.finish("验证🐎错误！")
            headers["Authorization"] = resp.headers["Authorization"]
            print(resp.headers["Authorization"])
            await session.send(cq.reply(session.event.message_id) + "正确！")
            imgdata = base64.b64decode(session.state["imageBase64"])
            file = open("/root/image/{}.jpg".format(session.state["img"].lower()), "wb")
            file.write(imgdata)
            file.close()


@login.args_parser
async def _123(session: CommandSession):
    session.state[session.current_key] = session.current_arg_text.strip()


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


@on_command("st", aliases={}, patterns="^st(0-9)*", only_to_me=False)
async def st(session: CommandSession):
    if session.is_first_run:
        msg = session.current_arg.strip()
        msg = re.sub("^st", "", msg)
        try:
            session.state["SanityLevel"] = int(msg) if msg != "" else 0
        except:
            session.finish()

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

    if "search" in session.state:
        if session.event.detail_type == "group":
            if await cksafe(session.event.group_id):
                session.state["SanityLevel"] = 4
            else:
                session.state["SanityLevel"] = 10
        res, _id = await searchPic(
            session.state["search"], session.state["SanityLevel"]
        )
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

    elif len(session.current_arg_images) == 0:
        if session.current_arg_text.strip() != "":
            session.state["search"] = session.current_arg_text
        else:
            session.finish("嘛，什么都没输入嘛～～")
    else:
        session.state["url"] = session.current_arg_images[0]


@on_command("来份涩图", patterns="^来.*份.*(涩|色)图", only_to_me=False)
async def sst(session: CommandSession):
    msg = session.current_arg_text.strip()
    if session.event.detail_type == "group":
        safe = await cksafe(session.event.group_id)
    else:
        safe = False
    if ("r18" in msg or "R18" in msg) and not safe:
        parm["r18"] = 1
    else:
        parm["r18"] = 0
    async with aiohttp.ClientSession() as sess:
        async with sess.get(api, params=parm) as resp:
            if resp.status != 200:
                session.finish("网络错误：" + str(resp.status))
            ShitJson = await resp.json()
            if ShitJson["quota"] == 0:
                session.finish(
                    f"返回码：{ShitJson['code']}\napi调用额度已耗尽，距离下一次调用额度恢复还剩 {ShitJson['quota_min_ttl']+1} 秒。"
                )
            data = ShitJson["data"][0]
            _id = await session.send(
                """发送中，。，。，。\npixiv id:{}\ntitle:{}\n作者:{}\ntgas:{}""".format(
                    data["pid"],
                    data["title"],
                    data["author"],
                    "、".join(["#" + i for i in data["tags"]]),
                ),
                at_sender=True,
            )
            print("1232312321")
            print(cq.image(ShitJson["data"][0]["url"]))
            await session.send(cq.image(ShitJson["data"][0]["url"]))


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


async def searchPic(key_word: str, maxSanityLevel: int = 4):
    datas = {
        "keyword": key_word,
        "pageSize": 15,
        "page": 1,
        "searchType": "original",
        "illustType": "illust",
        "maxSanityLevel": maxSanityLevel,
    }
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
            pixivicurl + "illustrations", params=datas, headers=headers
        ) as resp:
            if resp.status != 200:
                return (
                    f"网络 {resp.status} 错误哦，咕噜灵波～(∠・ω< )⌒★\n\n如果是401错误，请回复 login 来帮忙识别一下验证🐎哦",
                    0,
                )
            ShitJson = await resp.json()
        _id = None
        Good = [ind for ind in range(0, len(ShitJson["data"]))]
        try:
            while len(Good) != 0:
                pics = ShitJson["data"]
                ind = random.randint(0, len(Good))
                ind = Good[ind]
                res = await sendpic(
                    sess,
                    imageProxy(pics[ind]["imageUrls"][0]["large"], "img.cheerfun.dev"),
                    headers=headers,
                )
                if "失败" in res:
                    if "404" in res:
                        Good.remove(ind)
                        continue
                    else:
                        res = cq.image(
                            imageProxy_cat(pics[ind]["imageUrls"][0]["large"])
                        )
                _id = pics[ind]["id"]
                break
        except KeyError:
            res = f"暂时没有 {key_word} 的结果哦～"
        if _id == None:
            res = f"暂时没有 {key_word} 的结果哦～"
        return (
            res,
            _id if _id != None else res,
        )


async def getRelated(_id, ind=-1):
    datas = {"type": "related", "id": _id}
    random.seed(datetime.datetime.now())
    async with aiohttp.ClientSession() as sess:
        async with sess.get(searchapi, params=datas) as resp:
            if resp.status != 200:
                return "网络错误哦，咕噜灵波～(∠・ω< )⌒★"
            ShitJson = await resp.json()
        if ind == -1 or ind >= len(ShitJson["illusts"]):
            ind = random.randint(0, len(ShitJson["illusts"]))
        try:
            res = cq.image(imageProxy(ShitJson["illusts"][ind]["image_urls"]["large"]))
        except:
            res = f"暂时没有 {_id} 的相关结果哦～"
        return (
            res,
            ShitJson["illusts"][ind]["id"] if ind < len(ShitJson["illusts"]) else -1,
        )
