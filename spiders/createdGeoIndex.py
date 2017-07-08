# -*- coding: utf-8 -*-

import pymongo
import redis

Redis = redis.StrictRedis('paradise.lgbt')

Mongo = pymongo.MongoClient(
    'paradise.lgbt',
    socketTimeoutMS=None,
    socketKeepAlive=True
)

Collection = Mongo['paradise']
Database = Collection['stores']

stores = Database.find({
    'latitude': {'$exists': True},
    'longitude': {'$exists': True},
    # 'geospatial': {'$exists': False}
})

for store in stores:
    if store['latitude'] and store['longitude']:
        # store['geospatial'] = {
        #     'type': "Point",
        #     'coordinates': [float(store['longitude']), float(store['latitude'])]
        # }

        res = Redis.geoadd('stores', float(store['longitude']), float(store['latitude']), store['hash'])

        # res = Database.update_one({'hash': store['hash']}, {'$set': store}, upsert=False)

        print("Processed %s[%s] => %s" % (store['name'], store['hash'], res))

