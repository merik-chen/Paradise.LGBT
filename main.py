# -*- coding: utf-8 -*-

import spiders.Config as config

import os
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


@app.route('/')
def index():
    return '''
    <h1>PARADISE</h1>
    <h4>In a higher place, an eternal place of pleasure and joy.</h4>
    <p>Hello</p>
    '''


@app.route('/api/nearBy/<float:lon>/<float:lat>/<int:radius>/<string:unit>')
def api_near_by(lon, lat, radius, unit):

    real_ip = request.headers.get('X-Real-IP')
    forwarded_ip = request.headers.get('X-Forwarded-For')

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

    mongo = pymongo.MongoClient(
        config.app_cfg['mongo']['address'],
        socketTimeoutMS=None,
        socketKeepAlive=True
    )

    collection = mongo['paradise']

    for store in search:
        store_detail = collection['stores'].find_one({'hash': store[0]}, {'_id': -1, 'name': 1, 'address': 1, 'telephone': 1})
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
    resp.headers['X-REAL-IP'] = real_ip
    resp.headers['X-Forwarded-For'] = forwarded_ip

    print(request.headers)

    return resp

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST'), port=int(os.environ.get('PORT')), debug=os.environ.get('DEBUG') == 'yes')
