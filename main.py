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

import dateutil.parser
import github

if __name__ == '__main__':

    token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
    owner = os.environ.get('UMS_OWNER', 'the-trump-dump')
    repo = os.environ.get('UMS_REPO', 'editor-view')
    file_name = os.environ.get('UMS_WORKFLOW_FILE_NAME', 'deploy.yml')
    github_client = github.SimpleGithubClient(token)
    actions = github_client.actions()

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
