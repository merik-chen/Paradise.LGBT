# -*- coding: utf-8 -*-

from ...database import database


def search_stores_by_name(name):
    find = database['elasticSearch'].search(
        index='stores',
        doc_type='store',
        body={
            'query': {
                'term': {
                    'name': name
                }
            }
        }
    )

    return find
