import typing

import datetime

import types
import db


class GithubActionsRunService(object):
    initialization_sql = \
        '''
           create table if not exists github_action_runs (
                id serial not null primary key, 
                owner varchar(255) not null , 
                repository varchar(255) not null, 
                updated_at timestamptz  not null 
            );
            
            CREATE UNIQUE INDEX if not exists hash ON github_action_runs(owner, repository);
        '''.strip().split(';')

    def __init__(self, connection_builder: types.LambdaType) -> None:
        self.connection_builder = connection_builder

        def callback(cursor):
            sql = [a.strip() for a in self.initialization_sql if a.strip() != '']
            for line in sql:
                cursor.execute(line)

        db.execute_in_transaction(self.connection_builder, callback)

    def write_run_for(self, owner: str, repository: str, dt: datetime.datetime) -> None:
        sql = '''
            insert into github_action_runs( owner, repository, updated_at )
            values( %s, %s, %s )
            on conflict (owner, repository)
            do update set updated_at = %s
        '''

        def callback(cursor):
            cursor.execute(sql, (owner, repository, dt, dt,))

        db.execute_in_transaction(self.connection_builder, callback)

    def read_run_for(self, owner: str, repository: str) -> typing.List[typing.Dict]:
        sql = 'select * from github_action_runs where owner = %s and repository = %s  limit 1 '

        def callback(cursor):
            cursor.execute(sql, (owner, repository))
            the_list = cursor.fetchall()
            if len(the_list) == 1:
                return the_list[0]
            return None

        return db.execute_in_transaction(self.connection_builder, callback)
