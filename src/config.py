import os
import json


AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.json')

with open(CONFIG_FILE) as f_in:
    config = json.load(f_in)


github_org = config['github']['organization']

course = config['course']
course_name = course['name']
course_year = course['year']

project = config['project']
project_id = project['id']
project_name = project['name']

airtable = config['airtable']
airtable_database = airtable['database']
airtable_table = airtable['table']