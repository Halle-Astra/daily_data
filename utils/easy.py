# 此文件主要是存放各类小工具，用于简化部分功能代码

import json
from loguru import logger

def read_json(file):
    try:
        f = open(file,encoding='utf-8')
        content = json.load(f)
        f.close()
        return content
    except:
        logger.exception("读取json文件 {} 失败".format(file))
