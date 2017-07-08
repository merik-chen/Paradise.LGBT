# -*- coding: utf-8 -*-

import redis
from flask import Flask, jsonify

app = Flask(__name__)

redis_pool = redis.ConnectionPool(host='paradise.lgbt')


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

    for store in search:
        near_by_stores['stores'].append({
            'storeHash': store[0],
            'distance': store[1],
            'geospatial': {
                'lon': store[2][0],
                'lat': store[2][1],
            }
        })

    return jsonify(near_by_stores)

if __name__ == '__main__':
    app.run()
