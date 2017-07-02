# -*- coding: utf-8 -*-
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
# print sys.path

import scrapy
from scrapy.conf import settings
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bson.binary import Binary
# import Database
import Commons
import urllib.request
import pprint
import random
import time
import json
import re


class IpeenSpider(CrawlSpider):

    # settings.set('LOG_LEVEL', 'DEBUG')  # WARNING
    settings.set('DOWNLOAD_DELAY', 3)

    name = "ipeen"
    allowed_domains = ["www.ipeen.com.tw"]
    start_urls = (
        'http://www.ipeen.com.tw/taiwan/channel/F',
    )

    # Collection = Database.Mongo['ipeen']
    #
    # links_db = Collection['stores']
    # index_db = Collection['links']

    rules = (
        #  http://www.ipeen.com.tw/search/taiwan/000/1-0-7-0/
        Rule(LinkExtractor(allow=('\/search\/taiwan\/000\/1-0-.+', )), callback='show_1', follow=True),
        Rule(LinkExtractor(allow=('\/shop\/\d+\-[\w\%]+$', )), callback='parse_article', follow=True),
    )

    custom_settings = {
        # 'LOG_LEVEL': 'DEBUG',
        # 'DOWNLOAD_DELAY': 5
    }

    def show_1(self, response):
        # self.index_db.update_one(
        #     {'link': response.url},
        #     {
        #         '$set': {
        #             'link': response.url,
        #             'hash': Commons.make_sha1(response.url.encode('utf-8'))
        #         }
        #     }, upsert=True
        # )
        print(response.url)

    def parse_article(self, response):

        store = {}.copy()

        article = response.css('article#shop')

        store['link'] = article.css('#shop::attr("itemid")').extract_first()

        if store['link']:

            store['hash'] = Commons.make_sha1(store['link'].encode('utf-8'))

            store['name'] = article.css('span[itemprop="name"]::text').extract_first()

            store['telephone'] = article.css('meta[itemprop="telephone"]::attr("content")').extract_first()
            store['description'] = article.css('meta[itemprop="description"]::attr("content")').extract_first()
            store['priceRange'] = article.css('meta[itemprop="priceRange"]::attr("content")').extract_first()
            store['locality'] = article.css('meta[itemprop="addressLocality"]::attr("content")').extract_first()
            store['region'] = article.css('meta[itemprop="addressRegion"]::attr("content")').extract_first()
            store['postalCode'] = article.css('meta[itemprop="postalcode"]::attr("content")').extract_first()
            store['streetAddress'] = article.css('meta[itemprop="streetAddress"]::attr("content")').extract_first()

            store['address'] = response.css('meta[property="ipeen_app:address"]::attr("content")').extract_first()

            store['latitude'] = response.css('meta[property="place:location:latitude"]::attr("content")').extract_first()
            store['longitude'] = response.css('meta[property="place:location:longitude"]::attr("content")').extract_first()

            store['image'] = article.css('img[itemprop="image"]::attr("src")').extract_first()
            if store['image']:
                img_res = urllib.request.urlopen(store['image']).read()
                if img_res:
                    # img_binary = StringIO(img_res)
                    store['image'] = Binary(img_res)

            store['breadcrumb'] = []

            for breadcrumb in response.css('#breadcrumb a[itemprop="url"]'):
                _type = breadcrumb.css('span[itemprop="title"]::text').extract_first()
                if _type:
                    if not(_type in store['breadcrumb']) and u'iPeen 愛評網' != _type:
                        store['breadcrumb'].append(_type)

            # self.links_db.update_one(
            #     {'link': store['link']},
            #     {
            #         '$set': store
            #     }, upsert=True
            # )

            print('saved', store['name'])
            pprint.pprint(store)
        else:
            print('skipped', response.url)

        # time.sleep(random.randrange(3, 5))
