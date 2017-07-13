# -*- coding: utf-8 -*-

import re
import json
import redis
import pymongo

from ..config import app_cfg

redis_client = redis.StrictRedis(app_cfg['redis']['address'])
mongodb = pymongo.MongoClient(
    host=app_cfg['mongo']['address'],
    socketTimeoutMS=None,
    socketKeepAlive=True
)

collection = mongodb['paradise']


def is_cjk(character):
    """"
    Checks whether character is CJK.

        >>> is_cjk(u'\u33fe')
        True
        >>> is_cjk(u'\uFE5F')
        False

    :param character: The character that needs to be checked.
    :type character: char
    :return: bool
    """
    return any([start <= ord(character) <= end for start, end in
                [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215),
                 (63744, 64255), (65072, 65103), (65381, 65500),
                 (131072, 196607)]
                ])


def is_ascii(sentence):
    regex = r"^[A-Za-z0-9_-]*$"
    return re.match(regex, sentence)


def segment_string(text):
    regex = r"(\w+)\s?"

    matches = re.finditer(regex, text, re.IGNORECASE)

    split = []

    for match in matches:
        word = match.group().strip()
        if is_ascii(word):
            split.append(word)
        else:
            for num, character in enumerate(word):
                split.append(word[0:num+1])

    return split


if __name__ == '__main__':
    segment_string('吉米熊 Good Morning 早午餐')

