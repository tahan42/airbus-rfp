from flask import request, Blueprint
from flask import current_app as app
from datetime import datetime, timezone
import uuid
import json
from . import transformer


bp = Blueprint('ingester', __name__, url_prefix='/')


@bp.route("/ingest", methods=['POST'])
def ingest():
    '''
    {"event": {type: "metric","time":"1000000000.001","source":"test-source","sourcetype":"test-sourcetype","index":"myindex123","fields":{"_value":2.2,"metric_name":"test-metric_name","service":"test-service","hostname":"test-hostname","unit":"1","type":"g"}}}    
    '''
    if request.method == "POST":
        apply_transformers(request)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


def apply_transformers(request):
    d = datetime.now(timezone.utc)
    current_batch_id = '{}{}{}{}'.format(d.year, d.month, d.day, d.hour)
    ts = datetime.timestamp(d)
    raw_id = str(uuid.uuid4())
    raw_data = request.json

    # insert raw data and populate the redis stream needed by the forwarder
    transformer.RawData(raw_data, raw_id, ts).load()

    # apply relevant transformations for the current payload per type of event
    if raw_data['event'] == 'metric':
        transformer.ContextMetadata(raw_id, request.headers).load()
        transformer.ByHost(raw_data, raw_id, current_batch_id).load()
        transformer.ByIndex(raw_data, raw_id, current_batch_id).load()
        transformer.BySource(raw_data, raw_id, current_batch_id).load()
