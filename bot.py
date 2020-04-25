from os import path
import sys
import nonebot
from nonebot.log import logger
import logging
import db
import config
import config_d
import argparse

if __name__ == '__main__':

    paser = argparse.ArgumentParser()
    paser.add_argument('-d', '--debug', action='store_true', default=False)
    args = paser.parse_args(sys.argv[1:])

    if args.debug == True:
        nonebot.init(config_d)
    else:
        nonebot.init(config)
    file_handler = logging.FileHandler(
        path.join(path.dirname(__file__), 'log', 'mybot.log'))
    file_handler.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    bot = nonebot.get_bot()
    bot.server_app.before_serving(db.initdb)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'Pzzzzz', 'plugins'),
        'Pzzzzz.plugins'
    )
    nonebot.load_builtin_plugins()
    nonebot.run()

