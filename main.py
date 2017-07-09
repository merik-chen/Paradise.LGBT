# -*- coding: utf-8 -*-

import spiders.Config as config

import os
import json
import redis
import pymongo
from flask import Flask, jsonify, request, make_response
# from flask_pymongo import PyMongo

app = Flask(__name__)

redis_pool = redis.ConnectionPool(host=config.app_cfg['redis']['address'])

# app.config['MONGO_CONNECT'] = False
# app.config['MONGO_DBNAME'] = 'paradise'
# app.config['MONGO_URI'] = 'mongodb://%s:27017/' % config.app_cfg['mongo']['address']
#
# mongo = PyMongo(app)


def __get_store_by_redis(store_id, redis_client):
    __cache = redis_client.get("cache:store:%s" % store_id)
    if __cache:
        __cache = json.loads(__cache.decode('utf-8'))
    return __cache


def __get_store_by_mongodb(store_id, redis_client, collection):
    store_detail = collection['stores'].find_one({'hash': store_id}, {'_id': 0, 'image': 0})
    if store_detail:
        cache_key = "cache:store:%s" % store_id
        redis_client.set(cache_key, json.dumps(store_detail))
        redis_client.expire(cache_key, 60)
    return store_detail


def __get_store(store_id, redis_client, collection):
    __cached = __get_store_by_redis(store_id, redis_client)

    if __cached:
        __cached['cached'] = True
    else:
        __cached = __get_store_by_mongodb(store_id, redis_client, collection)

    return __cached


@app.route('/')
def index():
    return '''
    <h1>PARADISE</h1>
    <h4>In a higher place, an eternal place of pleasure and joy.</h4>
    <p>Hello</p>
    '''


@app.route('/api/nearBy/<float:lon>/<float:lat>/<int:radius>/<string:unit>')
def api_near_by(lon, lat, radius, unit):

    redis_client = redis.Redis(connection_pool=redis_pool)
    search = redis_client.georadius(
        'stores',
        longitude=lon,
        latitude=lat,
        radius=radius,
        unit=unit,
        withdist=True,
        withcoord=True,
        sort='ASC'
    )

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

    mongodb = pymongo.MongoClient(
        config.app_cfg['mongo']['address'],
        socketTimeoutMS=None,
        socketKeepAlive=True
    )

    collection = mongodb['paradise']

    for store in search:
        store_detail = __get_store(store[0], redis_client, collection)
        if store_detail:
            near_by_stores['stores'].append({
                'hash': store[0],
                'name': store_detail['name'],
                'address': store_detail['address'],
                'telephone': store_detail['telephone'],

                'distance': store[1],
                'geospatial': {
                    'lon': store[2][0],
                    'lat': store[2][1],
                }
            })

    resp = make_response(jsonify(near_by_stores))
    resp.headers['X-REAL-IP'] = request.remote_addr
    resp.headers['X-IS-SECURE'] = request.is_secure

    return resp

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST'), port=int(os.environ.get('PORT')), debug=os.environ.get('DEBUG') == 'yes')
