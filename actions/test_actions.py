import unittest
import os
import pg8000
import actions
import datetime


class GithubActionsRunServiceTest(unittest.TestCase):

    owner = 'joshlong'
    repository = 'simple-python-github-client-test'

    def setUp(self) -> None:
        db = os.environ.get('UMS_DB_NAME', 'ttd')
        host = os.environ.get('UMS_DB_HOST', 'localhost')
        username = os.environ.get('UMS_DB_USERNAME', 'orders')
        pw = os.environ.get('UMS_DB_PASSWORD', 'orders')

        self.db_connection = pg8000.connect(username, password=pw, database=db, host=host)
        self.github_actions_db_service = actions.GithubActionsRunService(self.db_connection)

    def test_write_run_for(self):
        now = datetime.datetime.now()
        self.github_actions_db_service.write_run_for(self.owner, self.repository, now)
