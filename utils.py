from nonebot import on_command, CommandSession

doc={'mrfz':'明日方舟','bcr':'公主链接 B服'}

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
        elif thing[i] not in [' ', '-']:
            sw = ""

    if sw == "" or len(sw) != 12:
        sw = '-1'

    return sw

