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

