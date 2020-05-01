from os import path
import sys
import nonebot
import db
import config
import config_debug
import argparse
from utils import init

if __name__ == "__main__":

    paser = argparse.ArgumentParser()
    paser.add_argument("-d", "--debug", action="store_true", default=False)
    args = paser.parse_args(sys.argv[1:])

    if args.debug == True:
        nonebot.init(config_debug)
    else:
        nonebot.init(config)

    init()

    bot = nonebot.get_bot()
    bot.server_app.before_serving(db.initdb)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), "Pzzzzz", "plugins"), "Pzzzzz.plugins"
    )
    nonebot.load_builtin_plugins()
    nonebot.run()
