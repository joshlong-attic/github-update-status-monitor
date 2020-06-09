import datetime
import unittest

import actions
import db
import main


class GithubActionsRunServiceTest(unittest.TestCase):
    owner = 'joshlong'
    repository = 'simple-python-github-client-test'

    def setUp(self) -> None:
        def reset(cursor):
            cursor.execute('drop table if exists github_action_runs')

        db.execute_in_transaction(main.build_connection, reset)
        self.github_actions_db_service = actions.GithubActionsRunService(main.build_connection)

    def test_write_run_for(self):
        now = datetime.datetime.now()
        result = self.github_actions_db_service.read_run_for(self.owner, self.repository)
        self.assertIsNone(result)
        self.github_actions_db_service.write_run_for(self.owner, self.repository, now)
        id, owner, repo, updated_at = self.github_actions_db_service.read_run_for(self.owner, self.repository)
        print('the id is', id, 'and the owner is', owner, 'and the repository is', repo, 'and it was updated at',
              updated_at)
