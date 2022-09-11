import json
import base64


def extract_body(event):
    if 'body' not in event:
        return {}

    raw = event['body']

    base64_needed = event.get('isBase64Encoded', False)
    if base64_needed:
        raw = base64.b64decode(raw).decode('utf-8')

    decoded = json.loads(raw)
    return decoded
