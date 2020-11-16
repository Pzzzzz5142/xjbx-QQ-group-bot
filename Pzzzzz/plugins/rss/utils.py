from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape, escape
import asyncio
from aiocqhttp.exceptions import Error as CQHttpError
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from db import db
import cq
import feedparser as fp
import re
import aiohttp
from utils import doc, hourse, sendpic


locks = {}


async def handlerss(
    bot,
    source,
    getfun,
    is_broadcast: bool = True,
    is_fullText: bool = False,
    broadcastgroup: list = [],
):
    loop = asyncio.get_event_loop()
    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = '{source}';""")
        if len(values) == 0:
            await conn.execute(f"""insert into rss values ('{source}','-1')""")
            db_dt = "-1"
        else:
            db_dt = values[0]["dt"]
        kwargs = {}
        if "pixiv" in source:
            kwargs["mode"] = source[len("pixiv_") :]
        try:
            ress = await getfun(**kwargs)
        except:
            await bot.send_private_msg(
                user_id=545870222, message=f"rss「{doc[source]}」更新出现异常"
            )
            logger.error(f"rss「{source}」更新出现异常", exc_info=True)
            return

        res, dt, lk, _ = ress[0]
        if dt == "Grab Rss Error!":
            await bot.send_private_msg(
                user_id=545870222, message=f"rss「[{doc[source]}]」更新出现异常"
            )
            logger.error(f"rss「{source}」更新出现异常", exc_info=True)
            return
        if dt != db_dt:
            preview = f"{doc[source]} - {source}:"
            mx = 5
            for item in ress:
                if item[1] != db_dt:
                    mx -= 1
                    preview += "\n"
                    preview += item[-1]
                    preview += "\n▲" + item[2]
                    if mx == 0:
                        break
                else:
                    break
            await conn.execute(f"update rss set dt = '{dt}' where id = '{source}'")
            await conn.execute(f"update rss set pre = '{db_dt}' where id = '{source}'")
            if is_broadcast:
                try:
                    for gp_id in broadcastgroup:
                        await bot.send_group_msg(
                            group_id=gp_id,
                            message=res[0]
                            if is_fullText
                            else preview + f"\n\n回复 rss {source} 获取详细信息",
                        )
                except CQHttpError:
                    pass

        values = await conn.fetch(
            f"""select qid, dt from subs where rss = '{source}'; """
        )
        for item in values:
            if item["dt"] != dt:
                asyncio.run_coroutine_threadsafe(
                    sendrss(item["qid"], bot, source, ress), loop,
                )


# num 第一个表示最获取的消息数，第二个表示在此基础上查看的消息数
# -1表示最大，-2表示到已读为止。
async def sendrss(
    qid: int,
    bot,
    source: str,
    ress=None,
    getfun=None,
    num=(-2, 3),
    route=None,
    feedBack=False,
):
    isP = "pixiv" in source
    if qid not in locks:
        locks[qid] = asyncio.Lock()
    async with locks[qid]:
        async with db.pool.acquire() as conn:
            values = await conn.fetch(
                f"""select dt from subs where qid={qid} and rss='{source}';"""
            )
            if len(values) > 0:
                qdt = values[0]["dt"]
            else:
                values = await conn.fetch(
                    f"""select pre from rss where id='{source}';"""
                )
                qdt = values[0]["pre"]
            cnt = 0
            is_read = False
            if ress == None:
                kwargs = {}
                if "pixiv" in source:
                    kwargs["mode"] = source[len("pixiv_") :]
                else:
                    kwargs["max_num"] = num[0] if num[0] != -2 else -1
                if route != None:
                    ress = await getfun(route, (num[0] if num[0] != -2 else -1))
                else:
                    ress = await getfun(**kwargs)
            if num[0] == -2:
                for i in range(len(ress)):
                    if ress[i][1] == qdt:
                        if i == 0:
                            try:
                                ress = ress[:1]
                            except:
                                ress = ress
                            break
                        ress = ress[:i]
                        break
            if num[1] != -1:
                ress = ress[: min(len(ress), num[1])]

            success_dt = ""
            fail = 0
            for res, dt, link, _ in reversed(ress):
                if is_read == False and dt == qdt:
                    is_read = True
                if num[1] != -1 and cnt >= num[1]:
                    break
                see = ""
                is_r = is_read
                cnt += 1
                if isP:
                    await asyncio.sleep(1)
                await bot.send_private_msg(user_id=qid, message="=" * 19)
                for text in res:
                    see = text
                    try:
                        await bot.send_private_msg(
                            user_id=qid, message=("已读：\n" if is_r else "") + text
                        )
                        if "[CQ:image" in text and not isP:
                            await asyncio.sleep(1)
                        is_r = False
                        success_dt = dt
                    except CQHttpError:
                        fail += 1
                        logger.error(f"Not ok here. Not ok message 「{see}」")
                        logger.error(f"Processing QQ 「{qid}」, Rss 「{source}」")
                        logger.error("Informing Pzzzzz!")
                        try:
                            await bot.send_private_msg(
                                user_id=545870222,
                                message=f"Processing QQ 「{qid}」, Rss 「{source}」 error! ",
                            )
                        except:
                            logger.error("Inform Pzzzzz failed. ")
                        logger.error("Informing the user!")
                        try:
                            await bot.send_private_msg(
                                user_id=qid,
                                message=f"该资讯发送不完整！丢失信息为：「{see}」，请联系管理员。"
                                + ("\n该消息来源：" + link if link != "" else "该资讯link未提供"),
                                auto_escape=True,
                            )
                        except:
                            try:
                                await bot.send_private_msg(
                                    user_id=qid,
                                    message=f"该资讯发送不完整！丢失信息无法发送，请联系管理员。这可能是由于消息过长导致的"
                                    + (
                                        "\n该消息来源：" + link
                                        if link != ""
                                        else "该资讯link未提供"
                                    ),
                                    auto_escape=True,
                                )
                            except:
                                logger.error("Informing failed!")
                        success_dt = dt

            try:
                await bot.send_private_msg(user_id=qid, message="=" * 19)
            except CQHttpError:
                pass
            try:
                await bot.send_private_msg(
                    user_id=qid,
                    message=f"已发送 {cnt} 条「{doc[source] if source !='自定义路由' else route}」的资讯！{f'其中失败 {fail} 条！' if fail !=0 else ''}咕噜灵波～(∠・ω< )⌒★",
                )
            except CQHttpError:
                logger.error(f"Send Ending Error! Processing QQ 「{qid}」")
            if success_dt != "" and source != "自定义路由":
                await conn.execute(
                    f"""update subs set dt = '{success_dt}' where qid = {qid} and rss = '{source}';"""
                )
    if feedBack:
        await bot.send_group_msg(
            group_id=feedBack, message=cq.at(qid) + f"「{doc[source]}」的资讯已私信，请查收。"
        )


async def getrss(route: str, max_num: int = -1):
    if route[0] == "/":
        route = route[1:]
    thing = fp.parse(r"http://172.18.0.1:1200/" + route)

    ress = [
        (
            ["暂时没有资讯哦，可能是路由不存在！"],
            thing["entries"][0]["title"] if len(thing["entries"]) > 0 else "something",
            "",
        )
    ]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        text = item.title + ("\n" + hourse(item["link"]) if "link" in item else "f")

        text = [text]

        ress.append((text, item["published"] if "published" in item else item.title))

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress


async def rssBili(uid, max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/bilibili/user/dynamic/" + str(uid))

    ress = [
        (
            ["暂时没有有用的新资讯哦！"],
            (
                thing["entries"][0]["title"]
                if len(thing["entries"]) > 0
                else "Grab Rss Error!"
            ),
            "",
        )
    ]

    cnt = 0

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        if (
            ("封禁公告" in item.summary)
            or ("小讲堂" in item.summary)
            or ("中奖" in item.summary)
        ):
            continue

        fdres = re.match(r".*?<br>", item.summary, re.S)

        if fdres == None:
            text = item.summary
        else:
            text = fdres.string[int(fdres.span()[0]) : fdres.span()[1] - len("<br>")]

        while len(text) > 1 and text[-1] == "\n":
            text = text[:-1]

        pics = re.findall(
            r"https://(?:(?!https://).)*?\.(?:jpg|jpeg|png|gif|bmp|tiff|ai|cdr|eps)\"",
            item.summary,
            re.S,
        )
        text = [text]

        async with aiohttp.ClientSession() as sess:
            for i in pics:
                i = i[:-1]
                pic = await sendpic(sess, i)
                if pic != None:
                    text.append(pic)
        ress.append(
            (
                text,
                item["published"],
                item["link"] if "link" in item and item["link"] != "" else "",
                item["title"],
            )
        )

        cnt += 1

    if len(ress) > 1:
        ress = ress[1:]

    return ress


async def add_rss(name: str, owner: str = "sys"):
    async with db.pool.acquire() as conn:
        try:
            await conn.execute(f"""insert into rss values ('{name}','-1','{owner}')""")
        except:
            return "该名称已被占据，开通失败"
        return "ok"


def AutoReply(prompt, title, thing: list) -> str:
    res = "[CQ:json,data=" + escape(
        '{"app":"com.tencent.autoreply","desc":"","view":"autoreply","ver":"0.0.0.1","prompt":"['
        + prompt
        + ']","meta":{"metadata":{"title":"'
        + title
        + '","buttons":['
    )
    thing = [("a", "b")]
    tmp = [
        '{"slot":'
        + str(ind + 1)
        + ',"action_data":"'
        + i[0]
        + '","name":"'
        + i[1]
        + '","action":"notify"}'
        for ind, i in enumerate(thing)
    ]
    res += escape(
        ",".join(tmp)
        + '],"type":"guest","token":"LAcV49xqyE57S17B8ZT6FU7odBveNMYJzux288tBD3c="}},"config":{"forward":1,"showSender":1}}'
    )
    res += "]"
    return res

