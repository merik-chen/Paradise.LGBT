# -*- coding: utf-8 -*-

from . import *
from libraries.NestedBlueprint import NestedBlueprint
from modals.search.elasticsearch import stores

search = NestedBlueprint(api, 'search')


@search.route('/')
def search_index():
    return 'search index'


@search.route('/by/name/<string:name>')
def search_by_name(name):
    return flask_make_response(
        make_json(
            request.path,
            prepare_data(
                'stores',
                attributes=stores.search_stores_by_name(name)
            )
        )
    )
