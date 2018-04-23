# -*- coding: utf-8 -*-

from . import *


@api.route('/')
def index():
    return flask_make_response(
        make_json(
            request.path,
            errors=[
                {
                    'code': 404,
                    'title': 'Not Found'
                }
            ]
        ),
        code=404
    )


@api.route('/ping')
def ping():
    return flask_make_response(
        make_json(
            request.path,
            data=prepare_data(
                'ping',
                attributes={
                    'ping': 'pong'
                }
            )
        )
    )
