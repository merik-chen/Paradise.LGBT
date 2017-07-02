# -*- coding: utf-8 -*-
import sys
from os import path
sys.path.append(path.dirname(path.abspath(__file__)))

from Config import *
import pymongo
import redis

Mongo = pymongo.MongoClient(
    app_cfg['mongo'],
    socketTimeoutMS=None,
    socketKeepAlive=True
)
Collection = Mongo['stores']
Database = Collection['ipeen']

Redis = redis.Redis(host=app_cfg['redis']['address'])