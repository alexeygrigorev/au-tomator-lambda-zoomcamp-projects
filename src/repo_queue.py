
import json
import boto3
import config

sqs = boto3.client('sqs')


def add_repo(airtable_record):
    sqs.send_message(
        QueueUrl=config.queue_url,
        MessageBody=json.dumps(airtable_record)
    )


def poll_available_repo_from_queue():
    response = sqs.receive_message(
        QueueUrl=config.queue_url, 
        MaxNumberOfMessages=1
    )
    
    if 'Messages' not in response:
        print(f'no repositories available in {config.queue_name}')
        return None

    messages = response['Messages']

    if len(messages) == 0:
        print(f'no repositories available in {config.queue_name}')
        return None

    message = messages[0]

    receipt_handle = message['ReceiptHandle']
    message_body = json.loads(message['Body'])

    fields = message_body['fields']

    repository_message = {
        'airtable_record': message_body,
        'sqs_receipt_handle': receipt_handle,
        'repository': {
            'name': fields['Project ID'],
            'url': fields['Project URL']
        },
    }

    print(f'pulled {fields["Project URL"]} from {config.queue_name}')

    return repository_message



def ack_repo_assigned(repository_message):
    if 'sqs_receipt_handle' not in repository_message:
        print('no receipt handle, returning without ack...')
        return

    handle = repository_message['sqs_receipt_handle']

    sqs.delete_message(
        QueueUrl=config.queue_url, 
        ReceiptHandle=handle,
    )