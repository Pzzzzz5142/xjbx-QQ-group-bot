import json


def packbili(url, title, preview, desc):
    title = (
        title.replace("&", "&amp")
        .replace(",", "&#44;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
        .replace('<em class="keyword">', "")
        .replace("</em>", "")
        .replace("\n", "\\n")
    )
    a = (
        '[CQ:json,data={"app":"com.tencent.structmsg"&#44;"config":{"autosize":true&#44;"forward":true&#44;"type":"normal"}&#44;"desc":"新闻"&#44;"extra":{"app_type":1&#44;"appid":100951776}&#44;"meta":{"news":{"action":""&#44;"android_pkg_name":""&#44;"app_type":1&#44;"appid":100951776&#44;"desc":"'
        + desc.replace("\n", "\\n")
        + '"&#44;"jumpUrl":"'
        + url
        + '"&#44;"preview":"'
        + preview
        + '"&#44;"source_icon":""&#44;"source_url":""&#44;"tag":"哔哩哔哩"&#44;"title":"'
        + title
        + '"}}&#44;"prompt":"&#91;来自🍺🍐🍺🍐的分享&#93;'
        + title
        + '"&#44;"ver":"0.0.0.1"&#44;"view":"news"}]'
    )
    return a

