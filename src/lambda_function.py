import os

import json
import boto3



def post_create_repository():
    response = {
        "response_type": "ephemeral",
        "text": "I need your email and github."
    }

    return response, 200


def lambda_handler(event, context):
    print(json.dumps(event))

    path = event["pathParameters"]["thepath"]
    method = event["requestContext"]["http"]["method"]

    response = {}
    status_code = 404

    if path == 'create_repository':
        if method == 'POST':
            response, status_code = post_create_repository()

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(response)
    }
