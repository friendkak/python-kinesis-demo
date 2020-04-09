import base64
import os
import json
import boto3  # AWS SDK

client = boto3.client('kinesis')
"""
This lambda takes a kinesis stream as input, parses the data, applies a filter, then ships the data to the destination kinesis stream.

"""
# get name of destination strem from ENV.  The ENV is populated with the name of the stream in the SAM template.
stream_name = os.environ.get('SINKSTREAM')


def lambda_handler(event, context):
    data = []
    # Records come as batches so we iterate the Records object
    for record in event['Records']:
        # decode base64 payload and parse the json
        payload = json.loads(base64.b64decode(record["kinesis"]["data"]))
        # if json payload matches our filter append it to the data array
        if payload['location']['state'] == "Colorado" or payload['location']['state'] == "Pennsylvania":
            # note we append the raw, encoded data instead of unmarshalling and base64 encoding our json blob for performance reasons.
            data.append({
                'Data': record["kinesis"]["data"],
                'PartitionKey': 'abazaba',
            })
    # Log filter data
    print(json.dumps(
        {"records": len(event['Records']), "filtered": len(data)}))
    # Don't attempt empty payloads
    if len(data) > 0:
        response = client.put_records(
            Records=data,
            StreamName=stream_name
        )
