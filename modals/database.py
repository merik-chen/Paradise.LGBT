# -*- coding: utf-8 -*-

import redis
import pymongo
from .config import config
from elasticsearch import Elasticsearch


class Mongodb:
    client = None
    collection = None

    def __init__(self, address='localhost', port=27017, default_collection='paradise'):
        self.client = pymongo.MongoClient(
            host=address, port=port,
            socketTimeoutMS=None,
            socketKeepAlive=True,
            connect=False
        )

        self.collection = self.client[default_collection]

database = {
    'elasticSearch': Elasticsearch(hosts=(config['elasticsearch']['address'])),
    'mongodb': Mongodb(address=config['mongodb']['address']),
    'pool': {
        'redis': redis.ConnectionPool(host=config['redis']['address'])
    }
}.copy()
