# -*- coding: utf-8 -*-
import sys
from os import path
sys.path.append(path.dirname(path.abspath(__file__)))

from Config import *
import pymongo
import redis

Mongo = pymongo.MongoClient(
    'localhost',
    socketTimeoutMS=None,
    socketKeepAlive=True
)
Collection = Mongo['paradise']
Database = Collection['stores']

Redis = redis.Redis(host=app_cfg['redis']['address'])
