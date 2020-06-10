# Github Update Status Monitor  

This service monitors upstream Github projects and - on their successful changes - triggers a redeploy of other services. 

## Configuring a Mapping 
You'll need to configure a mapping in the top level array in `mappings.json`. Each mapping contains a `source` - a Github repository whose Github Action workflow runs should be monitored - and a `target` - a Github repository whose Github Action workflow should be invoked.  

The mapping should look like this.

```json

    {
      "source": {
        "owner": "joshlong",
        "repository": "jwt-spring-boot-starter",
        "workflow_file_name": "build.yml"
      },
      "target": {
        "owner": "joshlong",
        "repository": "simple-python-github-client-test"
      }
    }
```

## Configuring the Downstream Repository to Respond to Dispatch Events 

This will send an repository dispatch event (arbitrarily named `update-event`) webhook to the Github Action. It won't do anything unless your Github Action is configured to respond to dispatch events. Make sure your Github Action includes something like the following. 


```yml

on:
  repository_dispatch:
    types: update-event  
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
```

## Running the Application

I run my Github Action monitor on... Github Actions! It's easy. Just configure it to run on a scheduled basis. It'll poll the other projects and issue events. Run it at whatever granularity you want. 

You could run it every 30 minutes. Here's my configuration to run it every 30 minutes, and on any `push` event or `pull_request` event.

```json 

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  schedule:
    - cron:  '0,30 * * * *'

```

## Configuring the Application

In order to deploy this service for your own purposes, you'll need to configure a few environment variables. If you're using Github Actions, these can be secrets or you can encode them (well, don't leave the password, anyway!) in the Github Action workflow file.

### Github Personal Access Token

You'll need to configure a `PERSONAL_ACCESS_TOKEN` environment varaible containing a personal access token which you can easily create on Github. Make sure to give it at least the `repo` permissions. 

### The Database 

You'll need several environment variables for your PostgreSQL database connection including the database name - sometimes called a schema (`GUSM_DB_NAME`),  the database host ( `GUSM_DB_HOST`), the database username (`GUSM_DB_USERNAME`), and the database password (`GUSM_DB_PASSWORD`)

