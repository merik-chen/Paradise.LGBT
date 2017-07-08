# -*- coding: utf-8 -*-

import redis
import pymongo

import Config

Redis = redis.StrictRedis(Config.app_cfg['redis']['address'])

Mongo = pymongo.MongoClient(
    Config.app_cfg['mongo']['address'],
    socketTimeoutMS=None,
    socketKeepAlive=True
)

Collection = Mongo['paradise']
Database = Collection['stores']

stores = Database.find({
    'latitude': {'$exists': True},
    'longitude': {'$exists': True},
})

for store in stores:
    if store['latitude'] and store['longitude']:
        if not store['geospatial']:
            store['geospatial'] = {
                'type': "Point",
                'coordinates': [float(store['longitude']), float(store['latitude'])]
            }
            res = Database.update_one({'hash': store['hash']}, {'$set': store}, upsert=False)

        res = Redis.geoadd('stores', float(store['longitude']), float(store['latitude']), store['hash'])

        print("Processed %s[%s] => %s" % (store['name'], store['hash'], res))

