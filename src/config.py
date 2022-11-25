import os
import redis
from flask import current_app, g


REDIS_DB_HOST = os.getenv('REDIS_DB_HOST') if os.getenv(
    'REDIS_DB_HOST') else ''
REDIS_DB_PORT = int(os.getenv('REDIS_DB_PORT')) if os.getenv(
    'REDIS_DB_PORT') else 12000
REDIS_DB_CERT_PATH = os.getenv('REDIS_DB_CERT_PATH') if bool(os.getenv(
    'REDIS_DB_CERT_PATH')) else ''
REDIS_POOL_MAX = int(os.getenv('REDIS_POOL_MAX')) if os.getenv(
    'REDIS_POOL_MAX') else 10
FORWARDER_STREAM = os.getenv('FORWARDER_STREAM') if os.getenv(
    'FORWARDER_STREAM') else 'forwader_stream'
FORWARDER_CONSUMER_GROUP = os.getenv('FORWARDER_CONSUMER_GROUP') if os.getenv(
    'FORWARDER_CONSUMER_GROUP') else 'forwader_cg'
def get_connection():
    if 'redis_pool' not in g:
        g.redis_pool = redis.ConnectionPool(
            max_connections=REDIS_POOL_MAX, 
            host=REDIS_DB_HOST, 
            port=REDIS_DB_PORT, 
            connection_class=redis.SSLConnection, 
            ssl_cert_reqs='required', 
            ssl_ca_certs=REDIS_DB_CERT_PATH)
    return redis.Redis(connection_pool=g.redis_pool)
