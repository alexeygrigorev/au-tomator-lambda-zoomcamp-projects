import os

import json
import boto3

import repositories
import lambda_util


def post_create_repository(body):
    email = body.get('email')
    if email is None:
        return 400, {'error': 'mandatory field "email" is missing'}

    github = body.get('github')
    if github is None:
        return 400, {'error': 'mandatory field "github" is missing'}

    status_code, response = repositories.assign_repository(
        github_name=github,
        email=email,
    )

    return status_code, response



def lambda_handler(event, context):
    print(json.dumps(event))

    path = event["pathParameters"]["thepath"]
    method = event["requestContext"]["http"]["method"]

    response = {}
    status_code = 404

    body = lambda_util.extract_body(event)

    if path == 'create_repository':
        if method == 'POST':
            status_code, response = post_create_repository(body)

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(response)
    }
