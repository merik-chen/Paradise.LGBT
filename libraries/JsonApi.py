# -*- coding: utf-8 -*-

import traceback


def prepare_data(_type, _id=None, attributes=None, relationships=None, meta=None):
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


def make_json(link, data=None, errors=None):
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

    return payload


def flask_make_response(data, code=200):
    try:
        from flask import jsonify, make_response
    except ImportError:
        print('Flask not installed')
        import json
        jsonify = json.dumps
        make_response = str

    try:
        return make_response(jsonify(data), code)
    except 'Exception':
        traceback.print_exc()
