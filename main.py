#!/usr/bin/env python

'''
Could this handle _all_ updates?

Perhaps this thing could read config all the time and then,
armed with the Github PAT, send a repository_dispatch event to the configured github repo?
https://help.github.com/en/actions/reference/events-that-trigger-workflows#external-events-repository_dispatch

We could perhaps configure it to check the latest run, then see when the
latest successful run is and then check it against the latest recorded successful run in a
database. We'd need a PostgreSQL database or something. Or even just a Redis instance.
'''

import os

import typing
import dateutil.parser
import github
import pg8000  # https://github.com/tlocke/pg8000
import json
import typing


class UpdateStatusService(object):

    def __init__(self, connection: pg8000.Connection) -> None:
        self.connection = connection


from dataclasses import dataclass


@dataclass
class EventMappingSource(object):
    owner: str
    repository: str
    workflow_file_name: str


@dataclass
class EventMappingDestination(object):
    owner: str
    repository: str


@dataclass
class EventMapping(object):
    source: EventMappingSource
    destination: EventMappingDestination


if __name__ == '__main__':

    def initialize_event_mappings() -> typing.List[EventMapping]:

        def is_empty(a_string: str):
            return a_string is not None and a_string.strip() == ''

        def get_owner_and_repository(json_obj: typing.Dict):
            owner = json_obj['owner']
            repository = json_obj['repository']
            assert not is_empty(owner), 'the source must be non-null'
            assert not is_empty(repository), 'the target must be non-null'
            return owner, repository

        def build_event_source(json_obj: typing.Dict) -> EventMappingSource:
            owner, repository = get_owner_and_repository(json_obj)
            return EventMappingSource(owner, repository, json_obj['workflow_file_name'])

        def build_event_target(json_obj: typing.Dict) -> EventMappingDestination:
            owner, repository = get_owner_and_repository(json_obj)
            return EventMappingDestination(owner, repository)

        with open('event-mappings.json') as json_file:
            json_str = json_file.read()
            obs = json.loads(json_str)['mappings']
            return [EventMapping(build_event_source(em_config['source']),
                                 build_event_target(em_config['target'])) for em_config in obs]


    event_mappings = initialize_event_mappings()
    print(event_mappings)

    # github
    github_token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
    # owner = os.environ.get('UMS_OWNER')
    # repo = os.environ.get('UMS_REPO')
    # file_name = os.environ.get('UMS_WORKFLOW_FILE_NAME', 'deploy.yml')

    # database connectivity
    db = os.environ.get('UMS_DB_NAME', 'ttd')
    pw = os.environ.get('UMS_DB_PASSWORD', 'orders')
    host = os.environ.get('UMS_DB_HOST', 'localhost')
    username = os.environ.get('UMS_DB_USERNAME', 'orders')


def old_main():

    #
    github_client = github.SimpleGithubClient(github_token)
    actions = github_client.actions()

    update_status_service = UpdateStatusService(
        pg8000.connect(username, password=pw, database=db, host=host))

    recent_runs = \
        actions.list_workflow_runs(owner=owner, repo=repo, workflow_file_name_or_id=file_name, status='success')[
            'workflow_runs']

    for r in recent_runs:
        print(r)
        status = r['status']
        conclusion = r['conclusion']
        if status == 'completed' and conclusion == 'success':
            last_run_datetime = dateutil.parser.parse(r['updated_at'])
            print(last_run_datetime)

    # figure out how to issue a repository dispatch
