import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

app_env = 'ENV' in os.environ and str(os.environ['ENV']).lower() or ''

if app_env == 'testing':
    app_cfg = {
        'mongo': {'address': 'paradise.mongo', 'port': 27017},
        'redis': {'address': 'paradise.lgbt', 'port': 6379},
    }
elif app_env == 'spider':
    app_cfg = {
        'mongo': {'address': 'paradise.mongo', 'port': 27017},
        'redis': {'address': '10.99.0.11', 'port': 6379},
    }
else:
    app_cfg = {
        'mongo': {'address': 'paradise.mongo', 'port': 27017},
        'redis': {'address': '127.0.0.1', 'port': 6379},
    }

