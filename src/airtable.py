import config

import requests


AIRTABLE_URL_TEMPLATE = "https://api.airtable.com/v0/{database}/{table}"

airtable_headers = {
    'Authorization': f'Bearer {config.AIRTABLE_TOKEN}'
}


def create_airtable_record(repository, student=None):
    record = {
        "Project ID": repository['name'],
        "Project URL": repository['url'],
        "Course": config.course_name,
        "Year": str(config.course_year),
        "Project": config.course_name,
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
    return reponse_json