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
import datetime
import github
# https://github.com/tlocke/pg8000
import mappings
import pg8000
import actions


def build_connection() -> pg8000.Connection:
    db = os.environ.get('UMS_DB_NAME', 'ttd')
    host = os.environ.get('UMS_DB_HOST', 'localhost')
    username = os.environ.get('UMS_DB_USERNAME', 'orders')
    pw = os.environ.get('UMS_DB_PASSWORD', 'orders')
    return pg8000.connect(username, password=pw, database=db, host=host)


if __name__ == '__main__':

    def key_generator(d: typing.Dict) -> int:
        return d['run_number']


    github_token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
    github_client = github.SimpleGithubClient(github_token)
    db_service = actions.GithubActionsRunService(build_connection)

    with open('event-mappings.json') as json_fp:
        event_mappings = mappings.EventMapping.read_event_mappings(json_fp)

        for em in event_mappings:
            recent_runs = github_client.actions().list_workflow_runs(
                owner=em.source.owner,
                repo=em.source.repository,
                workflow_file_name_or_id=em.source.workflow_file_name,
                status='success')['workflow_runs']
            successful_runs = [a for a in recent_runs if a['status'] == 'completed' and a['conclusion'] == 'success']
            successful_runs.sort(key=key_generator, reverse=True)
            latest_successful_run = successful_runs[0]
            updated_at = dateutil.parser.parse(latest_successful_run['updated_at'])
            db_row = db_service.read_run_for(em.source.owner, em.source.repository)

            def publish_event():
                print('publishing an update-event.', em.destination.owner, '/', em.destination.repository,
                      'has changed so invoking',
                      em.destination.owner, '/', em.destination.repository)
                github_client.repos().create_repository_dispatch_event(
                    em.destination.owner, em.destination.repository, 'update-event', '{}')
                db_service.write_run_for(em.source.owner, em.source.repository, datetime.datetime.now())


            if db_row is not None:
                _, _, _, db_updated_at = db_row
                if updated_at > db_updated_at:
                    publish_event()
            else:
                publish_event()
