import os, sys, time

source_repos = ['this-week-in-spring', 'the-trump-dump']
modules = ['bookmark-ingest-job', 'bookmark-api', 'bookmark-editor-view']
results = []

for sr in source_repos:
    for m in modules:
        content = f'''
          [
            "source": [
            "owner": "this-week-in",
            "repository": "{m}",
            "workflow_file_name": "deploy.yml"
          ],
          "target": [
            "owner": "{sr}",
            "repository": "{m}"
          ]
            ]
            '''

        content = content.replace('[', '{')
        content = content.replace(']', '}')
        # print('-' * 100)
        # print(content)
        results.append(content)

print(','.join(results))
