from os import path

import nonebot
from nonebot.log import logger
import logging

import config

if __name__ == '__main__':
    nonebot.init(config)
    file_handler = logging.FileHandler(
        path.join(path.dirname(__file__), 'log', 'mybot.log'))
    file_handler.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'Pzzzzz', 'plugins'),
        'Pzzzzz.plugins'
    )
    nonebot.load_builtin_plugins()
    nonebot.run()
