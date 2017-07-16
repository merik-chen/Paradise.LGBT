# -*- coding: utf-8 -*-

import spiders.Config as config

import os
import json
import redis
import pymongo
from flask import Flask, jsonify, request, make_response

from modals.geohash import decode_exactly, decode as geohash_decode, encode as geohash_encode

# from flask_pymongo import PyMongo

app = Flask(__name__)

redis_pool = redis.ConnectionPool(host=config.app_cfg['redis']['address'])


# app.config['MONGO_CONNECT'] = False
# app.config['MONGO_DBNAME'] = 'paradise'
# app.config['MONGO_URI'] = 'mongodb://%s:27017/' % config.app_cfg['mongo']['address']
#
# mongo = PyMongo(app)

database = {}


class Mongodb:
    client = None
    collection = None

    def __init__(self, address='localhost', port=27017):
        self.client = pymongo.MongoClient(
            host=address, port=port,
            socketTimeoutMS=None,
            socketKeepAlive=True,
            connect=False
        )

        self.collection = self.client['paradise']


database['mongodb'] = Mongodb(address=config.app_cfg['mongo']['address'])


def __prepare_resp_json_api(link, data):
    payload = {
        'links': {
            'self': link
        },
        'data': data,
    }
    return jsonify(payload)


def __record_near_by_logs(lon, lat, radius, unit, user_agents, ip, is_active=False):
    __logger = database['mongodb'].collection['log_geo_near_by']

    geo_hash = geohash_encode(latitude=lat, longitude=lon)

    __logger.update_one(
        {'geo_hash': geo_hash},
        {
            '$set': {
                'geo_hash': geo_hash,
                'location': {
                    'type': 'Point',
                    'coordinates': [lon, lat]
                },
            },
            '$push': {
                'logs.%s%s' % (radius, unit): {'ip': ip, 'user_agent': user_agents, 'active': is_active}
            }
        }, upsert=True
    )


def __get_store_by_redis(store_id, redis_client):
    __cache = redis_client.get("cache:store:%s" % store_id)
    if __cache:
        __cache = json.loads(__cache.decode('utf-8'))
    return __cache


def __get_store_by_mongodb(store_id, redis_client, collection):
    store_detail = database['mongodb'].collection['stores'].find_one({'hash': store_id}, {'_id': 0, 'image': 0})
    if store_detail:
        cache_key = "cache:store:%s" % store_id
        redis_client.set(cache_key, json.dumps(store_detail))
        redis_client.expire(cache_key, 60 * 60)
    return store_detail


def __get_store(store_id, redis_client, collection):
    __cached = __get_store_by_redis(store_id, redis_client)

    if __cached:
        __cached['cached'] = True
    else:
        __cached = __get_store_by_mongodb(store_id, redis_client, collection)

    return __cached


def __search_bear_by_use_mongodb(lon, lat, radius, unit, page, collection):
    if unit == 'km':
        radius = radius * 1000

    page = page <= 0 and 1 or page

    page -= 1
    skip = page * 50

    __store_ids = []

    __find = database['mongodb'].collection['stores'].find({
        'geospatial': {
            '$near': {
                '$geometry': {'type': "Point", 'coordinates': [lon, lat]},
                '$minDistance': 0,
                '$maxDistance': radius
            }
        }
    }, {
        '_id': 0,
        'hash': 1
    }, skip=skip, limit=50)

    for __store in __find:
        __store_ids.append(__store['hash'])

    return __store_ids


def __search_stores_by_name(query, page, is_blur, collection):
    __stores = {}.copy()

    page = page <= 0 and 1 or page

    page -= 1
    skip = page * 50

    if is_blur:
        query_string = "%s" % query
    else:
        query_string = "^%s" % query

    print(query_string)

    __find = database['mongodb'].collection['stores'].find(
        {'segment.name': {'$regex': query_string}},
        {'_id': 0, 'hash': 1, 'name': 1},
        skip=skip, limit=50
    )

    for __store in __find:
        __stores[__store['hash']] = __store['name']

    return __stores


def __get_stores_by_id(store_ids, redis_client, collection):
    stores = []
    for store in store_ids:
        store_detail = __get_store(store, redis_client, collection)
        if store_detail:
            stores.append({
                'hash': store,
                'name': store_detail['name'],
                'address': store_detail['address'],
                'telephone': store_detail['telephone'],

                'geospatial': {
                    'lon': store_detail['geospatial']['coordinates'][0],
                    'lat': store_detail['geospatial']['coordinates'][1],
                }
            })
    return stores


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

    near_by_stores['stores'] = __get_stores_by_id(search, redis_client, collection)

    resp = make_response(jsonify(near_by_stores))
    resp.headers['X-REAL-IP'] = request.remote_addr
    resp.headers['X-IS-SECURE'] = request.is_secure

    return resp


@app.route('/api/nearBy/<float:lon>/<float:lat>/<int:radius>/<string:unit>/<int:page>')
def api_near_by_pagination(lon, lat, radius, unit, page):
    __record_near_by_logs(lon, lat, radius, unit, request.user_agent.string, request.remote_addr, True)

    # mongodb = pymongo.MongoClient(
    #     config.app_cfg['mongo']['address'],
    #     socketTimeoutMS=None,
    #     socketKeepAlive=True
    # )

    redis_client = redis.Redis(connection_pool=redis_pool)
    # collection = mongodb['paradise']

    collection = None

    search = __search_bear_by_use_mongodb(lon, lat, radius, unit, page, collection)

    near_by_stores = {
        'config': {
            'range': radius,
            'unit': unit,
            'page': page
        },
        'center': {
            'lon': lon,
            'lat': lat
        },
        'stores': []
    }.copy()

    near_by_stores['stores'] = __get_stores_by_id(search, redis_client, collection)

    __data = {
        "type": "storeList",
        "id": None,
        'attributes': {
            'config': {
                'range': radius,
                'unit': unit,
                'page': page
            },
            'center': {
                'lon': lon,
                'lat': lat
            },
            'stores': __get_stores_by_id(search, redis_client, collection)
        }
    }

    __link = request.path.strip()

    resp = make_response(__prepare_resp_json_api(__link, __data))
    resp.headers['X-REAL-IP'] = request.remote_addr
    resp.headers['X-IS-SECURE'] = request.is_secure

    return resp


@app.route('/api/search/stores/by/name/<string:query>/<int:page>')
def api_search_store_by_name(query, page):
    mongodb = pymongo.MongoClient(
        config.app_cfg['mongo']['address'],
        socketTimeoutMS=None,
        socketKeepAlive=True
    )

    collection = mongodb['paradise']
    stores = __search_stores_by_name(query, page, False, collection)

    resp = make_response(jsonify(stores))
    resp.headers['X-IS-BLUR'] = False
    resp.headers['X-REAL-IP'] = request.remote_addr
    resp.headers['X-IS-SECURE'] = request.is_secure

    return resp


@app.route('/api/search/stores/by/name/<string:query>/<int:page>/blur')
def api_search_store_by_name_blur(query, page):
    mongodb = pymongo.MongoClient(
        config.app_cfg['mongo']['address'],
        socketTimeoutMS=None,
        socketKeepAlive=True
    )

    collection = mongodb['paradise']
    stores = __search_stores_by_name(query, page, True, collection)

    resp = make_response(jsonify(stores))
    resp.headers['X-IS-BLUR'] = True
    resp.headers['X-REAL-IP'] = request.remote_addr
    resp.headers['X-IS-SECURE'] = request.is_secure

    return resp


@app.route('/api/analytics/nearBy/<float:lon>/<float:lat>/<int:radius>/<string:unit>')
def api_analytics_near_by(lon, lat, radius, unit):
    __record_near_by_logs(lon, lat, radius, unit, request.user_agent.string, request.remote_addr)
    return jsonify({'status': True})


if __name__ == '__main__':
    app.run(host=os.environ.get('HOST'), port=int(os.environ.get('PORT')), debug=os.environ.get('DEBUG') == 'yes')
