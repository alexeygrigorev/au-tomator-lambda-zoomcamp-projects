import time
from typing import Dict, Tuple

import requests

import airtable
import repo_queue
import namesgenerator
import config


github_headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {config.GITHUB_TOKEN}' 
}


def generate_random_repo_name() -> str:
    course = config.course_name
    year = config.course_year
    project = config.project_id

    course_short = course.replace(' ', '').lower()
    project_prefix = f'{course_short}-{year}-{project:02d}-'

    random_name = namesgenerator.get_random_name(sep='-')
    final_repo_name = project_prefix + random_name
    
    return final_repo_name


def generate_repo_description() -> str:
    course = config.course_name
    year = config.course_year
    project_name = config.project_name
    return f"This is a {project_name} for {course} {year} (TODO: change it)"


def create_repo(repo_name: str, private: bool=True) -> str:
    repo_description = generate_repo_description()

    create_repo_request = {
        "name": repo_name,
        "description": repo_description,
        "private": private,
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False,
        "auto_init": True
    }

    org = config.github_org
    create_repo_url = f'https://api.github.com/orgs/{org}/repos'

    create_repo_response = requests.post(
        create_repo_url,
        json=create_repo_request,
        headers=github_headers,
    )

    create_repo_response.raise_for_status()

    response_json = create_repo_response.json()
    return response_json['html_url']


def make_repository_public(repo_name: str):
    patch_repo_request = {
        "private": False,
    }

    org = config.github_org
    patch_repo_url = f'https://api.github.com/repos/{org}/{repo_name}'

    patch_repo_response = requests.patch(
        patch_repo_url,
        json=patch_repo_request,
        headers=github_headers,
    )

    patch_repo_response.raise_for_status()

    response_json = patch_repo_response.json()
    print(f'{repo_name} is now public')

    return response_json['html_url']


def get_commit_sha_main(repo_name: str) -> str:
    org = config.github_org

    url = f'https://api.github.com/repos/{org}/{repo_name}/git/refs'

    refs_response = requests.get(url, headers=github_headers)
    refs_response.raise_for_status()

    response_json = refs_response.json()

    main_sha = response_json[0]['object']['sha']
    return main_sha


def create_branch(repo_name: str, branch_name: str, base_sha: str) -> str:
    org = config.github_org
    create_branch_url = f'https://api.github.com/repos/{org}/{repo_name}/git/refs'

    create_branch_request = {
        'ref': f'refs/heads/{branch_name}',
        'sha': base_sha
    }

    create_branch_response = requests.post(
        create_branch_url,
        json=create_branch_request,
        headers=github_headers
    )

    create_branch_response.raise_for_status()

    response_json = create_branch_response.json()
    branch_url = response_json["url"]

    return branch_url


def add_collaborator(repo_name: str, collaborator: str,
        permission: str="admin") -> str:
    org = config.github_org
    add_collaborator_url = f'https://api.github.com/repos/{org}/{repo_name}/collaborators/{collaborator}'

    add_collaborator_request = {
        "permission": "admin"
    }

    add_collaborator_response = requests.put(
        add_collaborator_url,
        headers=github_headers,
        json=add_collaborator_request
    )
    add_collaborator_response.raise_for_status()

    if add_collaborator_response.status_code == 204:
        print(f'{collaborator} is already a collaborator for {repo_name}')
        return None

    response_json = add_collaborator_response.json()
    invite_url = response_json['html_url']
    return invite_url


def create_pull_request(repo_name: str, target_branch: str):
    org = config.github_org
    pull_request_url = f'https://api.github.com/repos/{org}/{repo_name}/pulls'

    request = {
        "title": 'Project review', #f"Project review {i} by NAME #{i}",
        "body": "Here we will put a template",
        "head": "main",
        "base": target_branch
    }
    
    pull_request_response = requests.post(pull_request_url, json=request, headers=github_headers)
    pull_request_response.raise_for_status()

    json_response = pull_request_response.json()
    html_url = json_response['html_url']
    return html_url


def create_random_repo(private=True) -> Dict:
    repo_name = generate_random_repo_name()
    repository_url = create_repo(repo_name=repo_name, private=private)
    print(f'repository_url: {repository_url}, sleeping for 5 seconds')
    time.sleep(5)

    main_sha = get_commit_sha_main(repo_name)
    print(f'main sha: {main_sha}')
    time.sleep(5)

    for i in range(1, 4):
        branch_name = f'review_{i}'
        branch_url = create_branch(repo_name, branch_name, main_sha)
        print(f'created branch {branch_url}, sleeping for 5 seconds...')
        time.sleep(5)

    repository = {
        'name': repo_name,
        'url': repository_url,
        'private': private
    }

    return repository


def ensure_profile_exists(student: str):
    if student.startswith('https://'):
        error_code = 400
        error = {
            'error': 'provide GitHub username, not URL'
        }
        return error_code, error
    
    user_url = f"https://api.github.com/users/{student}"
    user_response = requests.get(user_url)

    if user_response.status_code == 404:
        error_code = 404
        error = {
            'error': 'GitHub user does not exist'
        }
        return error_code, error

    return 200, None



def create_private_unassigned_repo():
    repository = create_random_repo(private=True)

    airtable_record = airtable.create_airtable_record(
        repository=repository,
        student=None
    )

    repository_message = {
        'airtable_record': airtable_record,
        'repository': repository
    }

    return repository_message


def create_public_assigned_repo(student):
    repository = create_random_repo(private=False)

    airtable_record = airtable.create_airtable_record(
        repository=repository,
        student=student
    )

    repository_message = {
        'airtable_record': airtable_record,
        'repository': repository
    }

    return repository_message


def assign_repository(github_name: str, email: str) -> Tuple[int, Dict]:
    error_code, error = ensure_profile_exists(github_name)
    if error_code != 200:
        return error_code, error

    student = {
        'email': email,
        'github': github_name
    }

    repository_message = repo_queue.poll_available_repo_from_queue()

    if repository_message is not None:
        repository_name = repository_message['repository']['name']
        make_repository_public(repository_name)

        invite_link = add_collaborator(
            repo_name=repository_name,
            collaborator=github_name,
            permission='admin'
        )

        airtable.update_airtable_record(
            airtable_record=repository_message['airtable_record'],
            student=student
        )

    else:
        print(f"We don't have an available repository, creating a new one")
        repository_message = create_public_assigned_repo(student)
        repository_name = repository_message['repository']['name']

        invite_link = add_collaborator(
            repo_name=repository_name,
            collaborator=github_name,
            permission='admin'
        )

    response = {
        'repository': repository_message['repository'],
        'invite_link': invite_link
    }

    return 200, response