import typing

import pg8000
import datetime


class GithubActionsRunService(object):
    initialization_sql = \
        '''
       create table if not exists github_action_runs (
            id serial not null primary key, 
            owner varchar(255) not null , 
            repository varchar(255) not null, 
            updated_at timestamptz  not null 
        );
        
        CREATE UNIQUE INDEX if not exists hash ON github_action_runs ( owner, repository  );

        '''.strip().split(';')

    def __init__(self, connection: pg8000.Connection) -> None:
        self.connection = connection

        # how to do a transaction to aggregate all these writes?
        for sql in self.initialization_sql:
            if sql.strip() != '':
                print(sql)
                print('-' * 10)
                print(self.connection.run(sql))

    def write_run_for(self, owner: str, repository: str, dt: datetime.datetime) -> None:
        sql = '''
            insert into github_action_runs( owner, repository, updated_at )
            values (:owner, :repository, :updated_at_1)
            on conflict (owner, repository)
            do update set updated_at = :updated_at_2
        '''
        self.connection.run(sql, owner=owner, repository=repository, updated_at_1=dt, updated_at_2=dt)

    def read_run_for(self, owner: str, repository: str) -> typing.List[typing.Dict]:
        return self.connection.run(
            'select * from github_action_runs where owner = :owner and repository = :repository  limit 1 ',
            owner=owner, repository=repository)
