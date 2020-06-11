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

import datetime
import logging
import os
import sys
import typing

import dateutil.parser
import github
import pg8000

import actions
import mappings

logging.basicConfig(level=logging.DEBUG)


def build_connection() -> pg8000.Connection:
    db = os.environ.get('GUSM_DB_NAME', 'ttd')
    host = os.environ.get('GUSM_DB_HOST', 'localhost')
    username = os.environ.get('GUSM_DB_USERNAME', 'orders')
    pw = os.environ.get('GUSM_DB_PASSWORD', 'orders')
    return pg8000.connect(username, password=pw, database=db, host=host)


def key_generator(d: typing.Dict) -> int:
    return d['run_number']


def main(_: typing.List[str]):
    github_token = os.environ.get('PERSONAL_ACCESS_TOKEN')
    github_client = github.SimpleGithubClient(github_token)
    db_service = actions.GithubActionsRunService(build_connection)

    def handle_event_mapping(event_mapping: mappings.EventMapping):

        logging.info('-' * 100)
        logging.info(
            f"looking for source.owner {event_mapping.source.owner} and "
            f"source.repository {event_mapping.source.repository} "
            f"and workflow file name {event_mapping.source.workflow_file_name}")
        recent_runs_response = github_client.actions().list_workflow_runs(
            owner=event_mapping.source.owner,
            repo=event_mapping.source.repository,
            workflow_file_name_or_id=event_mapping.source.workflow_file_name,
            status='success')

        logging.info(recent_runs_response)

        if 'workflow_runs' in recent_runs_response:

            if 'total_count' in recent_runs_response and recent_runs_response['total_count'] == 0:
                logging.info(
                    f'There are no runs for {event_mapping.source.owner}/{event_mapping.source.repository}. Skipping.')
                return

            recent_runs = recent_runs_response['workflow_runs']
            successful_runs = [a for a in recent_runs if
                               a['status'] == 'completed' and a['conclusion'] == 'success']
            successful_runs.sort(key=key_generator, reverse=True)
            latest_successful_run = successful_runs[0]
            github_updated_at = dateutil.parser.parse(latest_successful_run['updated_at'])
            db_row = db_service.read_run_for(event_mapping.source.owner, event_mapping.source.repository)

            def publish_event():
                logging.info(
                    f'publishing an update-event from {event_mapping.source.owner}/ {event_mapping.source.repository} '
                    f'has changed so invoking {event_mapping.destination.owner}/{event_mapping.destination.repository}')
                response = github_client.repositories().create_repository_dispatch_event(
                    event_mapping.destination.owner, event_mapping.destination.repository, 'update-event',
                    {'timestamp': datetime.datetime.now().timestamp() * 1000})
                print(response.status_code)
                db_service.write_run_for(event_mapping.source.owner, event_mapping.source.repository,
                                         datetime.datetime.now())

            if db_row is not None:
                _, _, _, db_updated_at = db_row
                if github_updated_at > db_updated_at:
                    publish_event()
                else:
                    logging.info('the date is older. no need to run.')
            else:
                publish_event()

    with open('mappings.json') as json_fp:
        event_mappings = mappings.EventMapping.read_event_mappings(json_fp)

        for em in event_mappings:
            try:
                handle_event_mapping(em)
            except Exception as e:
                logging.error(e)


main(sys.argv)
