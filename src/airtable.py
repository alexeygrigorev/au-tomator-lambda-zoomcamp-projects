import re
import time 

import config

import requests


AIRTABLE_URL_TEMPLATE = "https://api.airtable.com/v0/{database}/{table}"

airtable_headers = {
    'Authorization': f'Bearer {config.AIRTABLE_TOKEN}'
}


def create_airtable_record(repository, student=None):
    print(f'creating airtable record for {repository=}, {student=}')
    record = {
        "Project ID": repository['name'],
        "Project URL": repository['url'],
        "Course": config.course_name,
        "Year": str(config.course_year),
        "Project": config.project_name,
        "Status": 'CREATED'
    }

    if student is not None:
        record['Student Email'] = student['email']
        record['GitHub Username'] = student['github']
        record['Status'] = 'ASSIGNED'

    airtable_request = {
        "records": [{
            "fields": record
        }]
    }

    airtable_url = AIRTABLE_URL_TEMPLATE.format(
        database=config.airtable_database,
        table=config.airtable_table
    )

    reponse = requests.post(
        airtable_url,
        json=airtable_request,
        headers=airtable_headers
    )

    reponse.raise_for_status()
    reponse_json = reponse.json()

    airtable_record = reponse_json['records'][0]
    
    print(f'saved {repository} to airtabe')
    if student is not None:
        print(f'assigned {repository} to {student}')

    return airtable_record


def update_airtable_record(airtable_record, student):
    print(f'updating status for {airtable_record=}, {student=}')
    airtable_record_id = airtable_record['id']

    patch_records = [{
        "id": airtable_record_id,
        "fields": {
            "GitHub Username": student['github'],
            "Student Email": student['email'],
            "Status": "ASSIGNED"
        }
    }]

    data = {
        "records": patch_records
    }

    airtable_url = AIRTABLE_URL_TEMPLATE.format(
        database=config.airtable_database,
        table=config.airtable_table
    )
    response = requests.patch(airtable_url,
        json=data,
        headers=airtable_headers
    )

    response.raise_for_status()

    print(f'assigned {airtable_record["fields"]["Project ID"]} to {student=}')


def get_all_records(include_sleep=True):
    filter_condition = f"""AND(
        {{Project}} = '{config.project_name}',
        {{Year}} = '{config.course_year}',
        {{Course}} = '{config.course_name}'
    )
    """.strip()

    filter_condition = re.sub('\s+', ' ', filter_condition)

    params = {
        'pageSize': 50,
        'filterByFormula': filter_condition
    }

    airtable_url = AIRTABLE_URL_TEMPLATE.format(
        database=config.airtable_database,
        table=config.airtable_table
    )
    
    response = requests.get(
        airtable_url,
        params=params,
        headers=airtable_headers
    )

    response.raise_for_status()
    
    result = response.json()
    records = result['records']
    
    for record in records:
        yield record

    while 'offset' in result:
        if include_sleep:
            time.sleep(0.2)

        params['offset'] = result['offset']

        response = requests.get(
            airtable_url,
            params=params,
            headers=airtable_headers
        )

        response.raise_for_status()

        result = response.json()
        records = result['records']

        for record in records:
            yield record