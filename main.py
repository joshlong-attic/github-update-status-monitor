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
import os
import sys
import typing

import dateutil.parser
import github
import pg8000

import actions
import mappings


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

    with open('mappings.json') as json_fp:
        event_mappings = mappings.EventMapping.read_event_mappings(json_fp)

        for em in event_mappings:

            recent_runs_response = github_client.actions().list_workflow_runs(
                owner=em.source.owner,
                repo=em.source.repository,
                workflow_file_name_or_id=em.source.workflow_file_name,
                status='success')

            if 'workflow_runs' in recent_runs_response:
                recent_runs = recent_runs_response['workflow_runs']
                successful_runs = [a for a in recent_runs if a['status'] == 'completed' and a['conclusion'] == 'success']
                successful_runs.sort(key=key_generator, reverse=True)
                latest_successful_run = successful_runs[0]
                github_updated_at = dateutil.parser.parse(latest_successful_run['updated_at'])
                db_row = db_service.read_run_for(em.source.owner, em.source.repository)

                def publish_event():
                    print('publishing an update-event from', em.source.owner, '/', em.source.repository,
                          'has changed so invoking', em.destination.owner, '/', em.destination.repository)
                    response = github_client.repositories().create_repository_dispatch_event(
                        em.destination.owner, em.destination.repository, 'update-event',
                        {'timestamp': datetime.datetime.now().timestamp() * 1000})
                    print(response.status_code)
                    db_service.write_run_for(em.source.owner, em.source.repository, datetime.datetime.now())

                if db_row is not None:
                    _, _, _, db_updated_at = db_row
                    if github_updated_at > db_updated_at:
                        publish_event()
                    else:
                        print('the date is older. no need to run.')
                else:
                    publish_event()


main(sys.argv)
