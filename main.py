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
# https://github.com/tlocke/pg8000
import mappings

if __name__ == '__main__':

    def key_generator(d: typing.Dict) -> int:
        return d['run_number']


    github_token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
    db = os.environ.get('UMS_DB_NAME', 'ttd')
    pw = os.environ.get('UMS_DB_PASSWORD', 'orders')
    host = os.environ.get('UMS_DB_HOST', 'localhost')
    username = os.environ.get('UMS_DB_USERNAME', 'orders')

    github_client = github.SimpleGithubClient(github_token)
    actions = github_client.actions()

    with open('event-mappings.json') as json_fp:
        event_mappings = mappings.EventMapping.read_event_mappings(json_fp)
        print(event_mappings)
        # foreach mapping:
        # check to see if there's a recent successful build.
        # if there is and it's newer than the last successful build
        # note it in the DB, trigger an event
        for em in event_mappings:
            recent_runs = actions.list_workflow_runs(
                owner=em.source.owner,
                repo=em.source.repository,
                workflow_file_name_or_id=em.source.workflow_file_name,
                status='success')['workflow_runs']
            successful_runs = [a for a in recent_runs if a['status'] == 'completed' and a['conclusion'] == 'success']
            successful_runs.sort(key=key_generator, reverse=True)
            latest_successful_run = successful_runs[0]
            updated_at = dateutil.parser.parse(latest_successful_run['updated_at'])

# def old_main():
#     #
#
#     update_status_service = UpdateStatusService(
#         pg8000.connect(username, password=pw, database=db, host=host))
#
#     recent_runs = \
#         actions.list_workflow_runs(owner=owner, repo=repo, workflow_file_name_or_id=file_name, status='success')[
#             'workflow_runs']
#
#     for r in recent_runs:
#         print(r)
#         status = r['status']
#         conclusion = r['conclusion']
#         if status == 'completed' and conclusion == 'success':
#             last_run_datetime = dateutil.parser.parse(r['updated_at'])
#             print(last_run_datetime)
#
#     # figure out how to issue a repository dispatch
