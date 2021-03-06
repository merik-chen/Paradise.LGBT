# -*- coding: utf-8 -*-

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


def __search_near_by_store_id_by_redis(lon, lat, radius, unit):
    return redis_client.georadius(
            'stores',
            longitude=lon,
            latitude=lat,
            radius=radius,
            unit=unit,
            withdist=True,
            withcoord=True,
            sort='ASC'
        )


def __get_store_by_redis(store_id):
    return redis_client.get("cache:store:%s" % store_id)


def __get_store_by_mongodb(store_id):

    store_detail = collection['stores'].find_one({'hash': store_id}, {'_id': 0, 'image': 0})

    if store_detail:
        cache_key = "cache:store:%s" % store_id
        redis_client.set(cache_key, json.dumps(store_detail))
        redis_client.expire(cache_key, 10)

    return store_detail


def __get_store(store_id):
    __cached = __get_store_by_redis(store_id)

    if __cached:
        __cached = json.loads(__cached.decode('utf-8'))
        __cached['cached'] = True
    else:
        __cached = __get_store_by_mongodb(store_id)

    return __cached


def search(lon, lat, radius, unit):

    __store_ids = __search_near_by_store_id_by_redis(lon, lat, radius, unit)

    near_by_stores = {
        'config': {
            'range': radius,
            'unit': unit
        },
        'center': {
            'lon': lon,
            'lat': lat
        },
        'stores': []
    }.copy()

    if __store_ids:
        for store_info in __store_ids:
            store_detail = __get_store(store_info[0])
            if store_detail:
                near_by_stores['stores'].append({
                    'hash': store_info[0],
                    'name': store_detail['name'],
                    'address': store_detail['address'],
                    'telephone': store_detail['telephone'],

                    'distance': store_info[1],
                    'geospatial': {
                        'lon': store_info[2][0],
                        'lat': store_info[2][1],
                    }
                })

    return near_by_stores
