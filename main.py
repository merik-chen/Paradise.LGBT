# -*- coding: utf-8 -*-

import spiders.Config as config

import os
import json
import redis
import pymongo
import traceback

from flask import Flask, jsonify, request, make_response
from modals.geohash import decode_exactly, decode as geohash_decode, encode as geohash_encode

app = Flask(__name__)


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


database = {
    'mongodb': Mongodb(address=config.app_cfg['mongo']['address']),
    'pool': {
        'redis': redis.ConnectionPool(host=config.app_cfg['redis']['address'])
    }
}.copy()


def __prepare_resp_data(_type, _id=None, attributes=None, relationships=None, meta=None):
    data = {
        'type': _type,
        'id': _id,
    }

    if attributes:
        data['attributes'] = attributes
    if relationships:
        data['relationships'] = relationships
    if meta:
        data['meta'] = meta

    return data


def __prepare_resp_json_api(link, data=None, errors=None):

    payload = {
        'links': {
            'self': link
        },
    }

    if (data is None) and (errors is None):
        payload['errors'] = [
            {
                'status': 400,
                'title': 'Required params not input'
            }
        ]
    elif data and (errors is None):
        payload['data'] = data
    elif (data is None) and errors:
        payload['errors'] = errors

    resp = make_response(jsonify(payload))
    resp.headers['Content-type'] = 'application/vnd.api+json'
    return resp


def __record_near_by_logs(lon, lat, radius, unit, user_agents, ip, is_active=False):

    result = {
        'done': True
    }

    try:
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
    except:
        result['done'] = False
        result['error'] = traceback.format_exc()

    return result


def __get_store_by_redis(store_id):
    redis_client = redis.Redis(connection_pool=database['pool']['redis'])
    __cache = redis_client.get("cache:store:%s" % store_id)
    if __cache:
        __cache = json.loads(__cache.decode('utf-8'))
    return __cache


def __get_store_by_mongodb(store_id):
    redis_client = redis.Redis(connection_pool=database['pool']['redis'])
    store_detail = database['mongodb'].collection['stores'].find_one({'hash': store_id}, {'_id': 0, 'image': 0})
    if store_detail:
        cache_key = "cache:store:%s" % store_id
        redis_client.set(cache_key, json.dumps(store_detail))
        redis_client.expire(cache_key, 60 * 60)
    return store_detail


def __get_store(store_id):
    __cached = __get_store_by_redis(store_id)

    if __cached:
        __cached['cached'] = True
    else:
        __cached = __get_store_by_mongodb(store_id)

    return __cached


def __search_bear_by_use_mongodb(lon, lat, radius, unit, page):
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


def __search_stores_by_name(query, page, is_blur):

    page = page <= 0 and 1 or page

    page -= 1
    skip = page * 50

    if is_blur:
        query_string = "%s" % query
    else:
        query_string = "^%s" % query

    print(query_string)

    __find = database['mongodb'].collection['stores'].find(
        {'segment.name': {'$regex': query_string}, 'geospatial': {'$exists': True}},
        {'_id': 0, 'hash': 1},
        skip=skip, limit=50
    )

    __store_ids = []

    for __store in __find:
        __store_ids.append(__store['hash'])

    return __store_ids


def __get_stores_by_id(store_ids):
    stores = []
    for store in store_ids:
        store_detail = __get_store(store)
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
    redis_client = redis.Redis(connection_pool=database['pool']['redis'])
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

    near_by_stores['stores'] = __get_stores_by_id(search)

    data = __prepare_resp_data(
        'storeList',
        attributes=near_by_stores
    )

    resp = __prepare_resp_json_api(
        request.path,
        data
    )

    return resp


@app.route('/api/nearBy/<float:lon>/<float:lat>/<int:radius>/<string:unit>/<int:page>')
def api_near_by_pagination(lon, lat, radius, unit, page):
    __record_near_by_logs(lon, lat, radius, unit, request.user_agent.string, request.remote_addr, True)

    search = __search_bear_by_use_mongodb(lon, lat, radius, unit, page)

    data = __prepare_resp_data(
        'storeList',
        attributes={
            'config': {
                'range': radius,
                'unit': unit,
                'page': page
            },
            'center': {
                'lon': lon,
                'lat': lat
            },
            'stores': __get_stores_by_id(search)
        }
    )

    resp = __prepare_resp_json_api(request.path.strip(), data)

    return resp


@app.route('/api/search/stores/by/name/<string:query>/<int:page>')
def api_search_store_by_name(query, page):
    search = __search_stores_by_name(query, page, False)

    data = __prepare_resp_data(
        'storeList',
        attributes={
            'stores': __get_stores_by_id(search)
        }
    )

    resp = __prepare_resp_json_api(request.path.strip(), data)

    return resp


@app.route('/api/search/stores/by/name/<string:query>/<int:page>/blur')
def api_search_store_by_name_blur(query, page):
    search = __search_stores_by_name(query, page, True)

    data = __prepare_resp_data(
        'storeList',
        attributes={
            'stores': __get_stores_by_id(search)
        }
    )

    resp = __prepare_resp_json_api(request.path.strip(), data)

    return resp


@app.route('/api/analytics/nearBy/<float:lon>/<float:lat>/<int:radius>/<string:unit>')
def api_analytics_near_by(lon, lat, radius, unit):
    result = __record_near_by_logs(lon, lat, radius, unit, request.user_agent.string, request.remote_addr)

    if result['done']:
        data = __prepare_resp_data(
            'recordResult',
            attributes={'done': result['done']}
        )

        resp = __prepare_resp_json_api(request.path.strip(), data)
    else:
        resp = __prepare_resp_json_api(request.path.strip(), errors=[result['error']])

    return resp


if __name__ == '__main__':
    app.run(host=os.environ.get('HOST'), port=int(os.environ.get('PORT')), debug=os.environ.get('DEBUG') == 'yes')
