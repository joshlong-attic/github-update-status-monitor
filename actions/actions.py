import typing

import pg8000
import datetime

import types


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

    # def execute_in_tx(self, callback: types.LambdaType):
    #     with sqlite3.connect(':memory:') as conn:
    #         curs = conn.cursor()
    #         try:
    #             pass  # SQL commands go here
    #         except Exception as e:
    #             print(e)
    #         finally:
    #             if curs:
    #                 curs.close()

    def __init__(self, connection: pg8000.Connection) -> None:
        self.connection = connection

        for sql in self.initialization_sql:
            if sql.strip() != '':
                self.connection.run(sql)
        self.connection.commit()

    def write_run_for(self, owner: str, repository: str, dt: datetime.datetime) -> None:
        sql = '''
            insert into github_action_runs( owner, repository, updated_at )
            values( :owner, :repository, :updated_at_1 )
            on conflict (owner, repository)
            do update set updated_at = :updated_at_2
        '''
        self.connection.run(sql, owner=owner, repository=repository, updated_at_1=dt, updated_at_2=dt)
        self.connection.commit()

    def read_run_for(self, owner: str, repository: str) -> typing.List[typing.Dict]:
        return self.connection.run(
            'select * from github_action_runs where owner = :owner and repository = :repository  limit 1 ',
            owner=owner, repository=repository)
