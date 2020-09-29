import aiohttp
import asyncio
import cq
from utils import imageProxy
import pytz
from datetime import datetime, timedelta


async def pixiv(mode: str = "day"):
    searchapi = r"https://api.imjad.cn/pixiv/v2/"

    now = datetime.now(pytz.timezone("Asia/Shanghai"))

    retry = 3

    now -= timedelta(days=2)

    ress = [([f"在尝试 {retry} 遍之后，还是没有爬到图片呢。。。"], "Grab Rss Error!", "", "")]

    datas = {"mode": mode, "type": "rank", "date": now.strftime("%Y-%m-%d")}

    async with aiohttp.ClientSession() as sess:

        while retry != 0:
            async with sess.get(searchapi, params=datas) as resp:
                if resp.status != 200:
                    return "网络错误哦，咕噜灵波～(∠・ω< )⌒★"
                ShitJson = await resp.json()
                if "illusts" in ShitJson:
                    break
                await asyncio.sleep(1)
            retry -= 1
        if "illusts" not in ShitJson:
            return ress

        res = []
        _id = -1
        for item in ShitJson["illusts"]:
            res.append(cq.image(imageProxy(item["image_urls"]["medium"])))
            _id = item["id"]
        ress.append((res, _id, "", ""))

    if len(ress) > 1:
        ress = ress[1:]

    return ress
