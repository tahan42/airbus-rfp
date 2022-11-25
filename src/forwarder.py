from . import config as redis_component
from . import transformer

import requests


def forward():
    # Get the data to be forwarded to splunk HEC
    stream_entry = redis_component.get_connection().xreadgroup(redis_component.FORWARDER_CONSUMER_GROUP,
                                                               'consumer-1',
                                                               {redis_component.FORWARDER_STREAM: '>'},
                                                               count=1)

    # Apply transformations if applicable
    transf = transformer.SecurityToken(stream_entry['key'], 'new_token')
    enriched = transf.transform()
    payload = transf.get_data()
    print(payload)
    print(enriched)

    # Forward to splunk HEC
    # requests.post("https://splunk:8088/services/collector/event",
    #                   json=payload,
    #                   verify=False,
    #                   headers=enriched
    #                   )
