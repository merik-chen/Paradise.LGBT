# -*- coding: utf-8 -*-

import pymongo

from spiders.Config import app_cfg
from modals.stores import store as segment

Mongo = pymongo.MongoClient(
    app_cfg['mongo']['address'],
    socketTimeoutMS=None,
    socketKeepAlive=True
)

Collection = Mongo['paradise']
Database = Collection['stores']

stores = Database.find({'segment.name': {'$exists': False}})

for store in stores:
    _segment = segment.segment_string(store['name'])
    res = Database.update_one({'hash': store['hash']}, {'$set': {'segment.name': _segment}}, upsert=False)
    print("Processed %s[%s] => %s" % (store['name'], store['hash'], res))
