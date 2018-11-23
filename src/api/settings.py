# -*- coding: utf-8 -*-
import os

CACHE_PERIOD = 120
DEBUG = os.getenv('DEBUG', False)
RIGSTAT_ONLINE_URL = 'http://rigstat.online/%s/rigs'
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = 6379
REDIS_DB = 1
