import os
import time
import unittest

from notificator import AdminClient


TEST_HOST = os.getenv('NOTIFICATOR_TEST_HOST', 'http://localhost:8001')
TEST_ADMIN_EMAIL = os.getenv('NOTIFICATOR_TEST_ADMIN_EMAIL')
TEST_ADMIN_PASSWORD = os.getenv('NOTIFICATOR_TEST_ADMIN_PASSWORD')


@unittest.skipUnless(
    TEST_ADMIN_EMAIL and TEST_ADMIN_PASSWORD,
    'Set NOTIFICATOR_TEST_ADMIN_EMAIL and NOTIFICATOR_TEST_ADMIN_PASSWORD to run integration tests.',
)
class AdminIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = AdminClient(
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD,
            host=TEST_HOST,
        )
        self.created_account_id = None

    def tearDown(self):
        if self.created_account_id is not None:
            try:
                self.client.delete_account(self.created_account_id)
            except Exception:
                pass

    def test_admin_login_and_account_crud(self):
        accounts = self.client.get_accounts()
        self.assertIsInstance(accounts, list)

        suffix = str(int(time.time() * 1000))
        account = self.client.create_account(
            name=f'sdk_test_{suffix}',
            nick='SDK Test',
        )
        self.created_account_id = account['id']

        self.assertEqual('SDK Test', account['nick'])
        self.assertIn('token', account)

        updated = self.client.update_account(
            self.created_account_id,
            name=f'sdk_test_updated_{suffix}',
            nick='SDK Test Updated',
            renew_token=True,
        )
        self.assertEqual('SDK Test Updated', updated['nick'])
        self.assertEqual(f'sdk_test_updated_{suffix}', updated['name'])
        self.assertIn('token', updated)

        self.client.delete_account(self.created_account_id)
        self.created_account_id = None


if __name__ == '__main__':
    unittest.main()
