from abc import ABC, abstractmethod
from redis.commands.json.path import Path

from . import config


class TransformerBase(ABC):
    redis_component = None

    def __init__(self):
        self.redis_component = config.get_connection()


class RawData(TransformerBase):
    key = None
    value = None

    def __init__(self, raw_data, raw_data_id, ts):
        super().__init__()
        self.key = raw_data_id
        self.data = raw_data
        self.ts = ts

    def load(self):
        self.redis_component.json().set(self.key, Path.root_path(), self.data)
        self.redis_component.xadd(config.FORWARDER_STREAM, {
                             'key': self.key, 'timestamp': self.ts})


class ContextMetadata(TransformerBase):
    '''
     Enrich raw data with additional information from the headers.
    '''
    key = None
    value = None

    def __init__(self, raw_data_id, request_headers):
        super().__init__()
        self.key = 'enriched:{}'.format(raw_data_id)
        self.data = {'ip': request_headers['Host'],
                     'agent': request_headers['User-Agent'],
                     'token': request_headers['Authorization']}

    def load(self):
        self.redis_component.hmset(self.key, self.data)


class ByHost(TransformerBase):
    '''
     Store the raw data indexed by the host that generated it.
    '''
    key = None
    value = None

    def __init__(self, raw_data, raw_data_id, current_batch_id):
        super().__init__()
        self.key = 'host:{}:{}'.format(
            raw_data['fields']['hostname'], current_batch_id)
        self.data = raw_data_id

    def load(self):
        self.redis_component.sadd(self.key, self.data)


class BySource(TransformerBase):
    key = None
    value = None

    def __init__(self, raw_data, raw_data_id, current_batch_id):
        super().__init__()
        self.key = 'source:{}:{}'.format(
            raw_data['source'], current_batch_id)
        self.data = raw_data_id

    def load(self):
        self.redis_component.sadd(self.key, self.data)


class ByIndex(TransformerBase):
    key = None
    value = None

    def __init__(self, raw_data, raw_data_id, current_batch_id):
        super().__init__()
        self.key = 'index:{}:{}'.format(
            raw_data['index'], current_batch_id)
        self.data = raw_data_id

    def load(self):
        self.redis_component.sadd(self.key, self.data)


class SecurityToken(TransformerBase):
    new_token = None

    def __init__(self, raw_data_id, new_token):

        self.raw_data_id = raw_data_id
        self.new_token = new_token

    def transform(self):
        key = 'enriched:{}'.format(self.raw_data_id)
        enriched = self.redis_component.hmget(key)
        enriched['token'] = self.new_token
        self.redis_component.hmset(key, enriched)
        return enriched

    def get_data(self):
        return self.redis_component.json().get(self.raw_data_id, Path.root_path())
