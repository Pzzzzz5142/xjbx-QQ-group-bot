from nonebot import on_command, CommandSession
from random import randint

doc = {"mrfz": "明日方舟", "bcr": "公主连接 B服", "gcores": "机核网", "loli": "弟弟君"}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
}


def isdigit(c: str) -> bool:
    try:
        c = int(c)
    except:
        return False
    return True


def swFormatter(thing: str):
    pre = None
    sw = ""

    for i in range(len(thing)):
        if isdigit(thing[i]):
            sw += thing[i]
        elif thing[i] not in [" ", "-"]:
            sw = ""

    if sw == "" or len(sw) != 12:
        sw = "-1"

    return sw


def hourse(url: str) -> str:
    a = url
    try:
        url = list(url)
        for i in range(5):
            url.insert(randint(0, len(url)), "🐎")
        url = "".join(url)
    except:
        url = "（打🐎失败，请复制到浏览器中打开，不要直接打开！）"+a

    return url
