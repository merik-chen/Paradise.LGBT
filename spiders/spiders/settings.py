# -*- coding: utf-8 -*-

# Scrapy settings for spiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import os

app_env = 'APP_ENV' in os.environ and str(os.environ['APP_ENV']).lower() or ''

if app_env == 'spider':
    app_cfg = {
        'mongo': {'address': '127.0.0.1', 'port': 27017},
        'redis': {'address': '127.0.0.1', 'port': 6379},
        'memcached': {'address': '127.0.0.1', 'port': 11211},
        'mongoReplica': ['127.0.0.1:27017']
    }
elif app_env == 'master':
    app_cfg = {
        'mongo': {'address': '127.0.0.1', 'port': 27017},
        'redis': {'address': '127.0.0.1', 'port': 6379},
        'memcached': {'address': '127.0.0.1', 'port': 11211},
        'mongoReplica': ['127.0.0.1:27017']
    }
else:
    app_cfg = {
        'mongo': {'address': '127.0.0.1', 'port': 27017},
        'redis': {'address': '127.0.0.1', 'port': 6379},
        'memcached': {'address': '127.0.0.1', 'port': 11211},
        'mongoReplica': ['127.0.0.1:27017']
    }


BOT_NAME = 'spiders'

SPIDER_MODULES = ['spiders.spiders']
NEWSPIDER_MODULE = 'spiders.spiders'
LOG_LEVEL = 'WARNING'
USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spiders (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
CONCURRENT_REQUESTS_PER_IP = 4

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
    'accept-encoding': 'gzip, deflate, sdch',
    'cookie': 'over18=1',
    'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'spiders.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'spiders.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'spiders.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

if app_env == 'spider':
    DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
    # Enables scheduling storing requests queue in redis.
    SCHEDULER = "scrapy_redis.scheduler.Scheduler"

    # Don't cleanup redis queues, allows to pause/resume crawls.
    SCHEDULER_PERSIST = True
    SCHEDULER_IDLE_BEFORE_CLOSE = 10

    REDIS_HOST = app_cfg['redis']['address']
    REDIS_PORT = app_cfg['redis']['port']
