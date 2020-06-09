import unittest
import os
import pg8000
import actions
import datetime
import db


class GithubActionsRunServiceTest(unittest.TestCase):
    owner = 'joshlong'
    repository = 'simple-python-github-client-test'

    def setUp(self) -> None:

        def build_connection() -> pg8000.Connection:
            db = os.environ.get('UMS_DB_NAME', 'ttd')
            host = os.environ.get('UMS_DB_HOST', 'localhost')
            username = os.environ.get('UMS_DB_USERNAME', 'orders')
            pw = os.environ.get('UMS_DB_PASSWORD', 'orders')
            return pg8000.connect(username, password=pw, database=db, host=host)

        def reset(cursor):
            cursor.execute('drop table if exists github_action_runs')

        db.execute_in_transaction(build_connection, reset)

        self.github_actions_db_service = actions.GithubActionsRunService(build_connection)

    def test_write_run_for(self):
        now = datetime.datetime.now()
        result = self.github_actions_db_service.read_run_for(self.owner, self.repository)
        self.assertIsNone(result)
        self.github_actions_db_service.write_run_for(self.owner, self.repository, now)
        id, owner, repo, updated_at = self.github_actions_db_service.read_run_for(self.owner, self.repository)
        print('the id is', id, 'and the owner is', owner, 'and the repository is', repo, 'and it was updated at',
              updated_at)

        # self.assertTrue( resu)
