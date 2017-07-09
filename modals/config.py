
from .bootstrap import *

app_cfg = {
    'mongo': {
        'address': os.environ.get('MONGO_ADDRESS', 'paradise.mongo'),
        'port': os.environ.get('MONGO_PORT', 27017)
    },
    'redis': {
        'address': os.environ.get('REDIS_ADDRESS', 'paradise.lgbt'),
        'port': os.environ.get('REDIS_PORT', 6379)
    },
}.copy()