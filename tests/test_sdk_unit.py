import unittest
from unittest.mock import patch

from notificator import AdminClient, Notificator, NotificatorAPIError
from notificator.base_client import BaseClient


def ok_payload(body):
    return {
        'message': 'OK',
        'code': 200,
        'details': [],
        'user_message': 'OK',
        'identifier': 'OK',
        'body': body,
    }


def err_payload(identifier='FAIL', message='Request failed', details=None):
    return {
        'message': message,
        'code': 400,
        'details': details or [],
        'user_message': message,
        'identifier': identifier,
        'body': None,
    }


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


class BaseClientTests(unittest.TestCase):
    @patch('requests.request')
    def test_request_returns_body_when_identifier_ok(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload({'value': 1}))

        client = BaseClient(host='http://localhost:8001')
        body = client._request('GET', '/api/example')

        self.assertEqual({'value': 1}, body)

    @patch('requests.request')
    def test_request_raises_api_error_when_identifier_not_ok(self, mock_request):
        mock_request.return_value = FakeResponse(
            err_payload('AUTH@REQUIRE_LOGIN', '需要登录', ['token expired'])
        )

        client = BaseClient(host='http://localhost:8001')

        with self.assertRaises(NotificatorAPIError) as ctx:
            client._request('GET', '/api/example')

        self.assertEqual('AUTH@REQUIRE_LOGIN', ctx.exception.identifier)
        self.assertEqual('需要登录', ctx.exception.message)
        self.assertEqual(['token expired'], ctx.exception.details)


class AdminClientTests(unittest.TestCase):
    @patch('requests.request')
    def test_login_stores_admin_token_from_response_body(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload({'token': 'admin-token'}))

        client = AdminClient(
            email='admin@example.com',
            password='password',
            host='http://localhost:8001',
            auto_login=False,
        )
        body = client.login()

        self.assertEqual({'token': 'admin-token'}, body)
        self.assertEqual('admin-token', client.token)

    @patch('requests.request')
    def test_get_accounts_uses_token_header(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload([]))

        client = AdminClient(
            email='admin@example.com',
            password='password',
            host='http://localhost:8001',
            auto_login=False,
        )
        client.token = 'admin-token'
        client.get_accounts()

        self.assertEqual('GET', mock_request.call_args.kwargs['method'])
        self.assertEqual(
            {'Token': 'admin-token'},
            mock_request.call_args.kwargs['headers'],
        )

    @patch('requests.request')
    def test_update_account_matches_backend_contract(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload({'id': 1}))

        client = AdminClient(
            email='admin@example.com',
            password='password',
            host='http://localhost:8001',
            auto_login=False,
        )
        client.token = 'admin-token'
        client.update_account(
            1,
            name='new-name',
            nick='new-nick',
            renew_token=True,
            token='override-token',
        )

        self.assertEqual('PUT', mock_request.call_args.kwargs['method'])
        self.assertEqual(
            {'id': 1},
            mock_request.call_args.kwargs['params'],
        )
        self.assertEqual(
            {'name': 'new-name', 'nick': 'new-nick', 'renew': True},
            mock_request.call_args.kwargs['json'],
        )
        self.assertEqual(
            {'Token': 'override-token'},
            mock_request.call_args.kwargs['headers'],
        )

    @patch('requests.request')
    def test_get_notificator_binds_account_auth_and_locale(self, mock_request):
        mock_request.side_effect = [
            FakeResponse(ok_payload({'token': 'admin-token'})),
            FakeResponse(ok_payload([
                {'id': 1, 'name': 'demo', 'nick': 'Demo', 'token': 'account-token'}
            ])),
        ]

        client = AdminClient(
            email='admin@example.com',
            password='password',
            host='http://localhost:8001',
        )
        notificator = client.get_notificator('demo', locale='en-US')

        self.assertIsInstance(notificator, Notificator)
        self.assertEqual('demo$account-token', notificator.auth)
        self.assertEqual('en-US', notificator.locale)


class NotificatorTests(unittest.TestCase):
    @patch('requests.request')
    def test_send_uses_auth_header_and_returns_body(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload({'request_id': 'rid-1'}))

        client = Notificator('demo', 'account-token', host='http://localhost:8001')
        body = client.clean().prepare_webhook('https://example.com/hook').send('text', 'hello')

        self.assertEqual({'request_id': 'rid-1'}, body)
        self.assertEqual(
            {'Auth': 'demo$account-token'},
            mock_request.call_args.kwargs['headers'],
        )
        self.assertEqual(
            {
                'message': {
                    'format': 'text',
                    'body': 'hello',
                    'locale': 'zh-CN',
                },
                'deliveries': [
                    {
                        'channel': 'webhook',
                        'target': 'https://example.com/hook',
                        'options': {},
                    }
                ],
            },
            mock_request.call_args.kwargs['json'],
        )

    @patch('requests.request')
    def test_mail_shortcut_builds_delivery_options(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload({'request_id': 'rid-2'}))

        client = Notificator('demo', 'account-token', host='http://localhost:8001')
        client.mail(
            'user@example.com',
            'text',
            'hello',
            title='Subject',
            footer_note='footer',
            recipient_name='User',
        )

        payload = mock_request.call_args.kwargs['json']
        self.assertEqual('mail', payload['deliveries'][0]['channel'])
        self.assertEqual('user@example.com', payload['deliveries'][0]['target'])
        self.assertEqual(
            {'recipient_name': 'User', 'footer_note': 'footer'},
            payload['deliveries'][0]['options'],
        )
        self.assertEqual('Subject', payload['message']['title'])

    @patch('requests.request')
    def test_ntfy_shortcut_builds_delivery_options(self, mock_request):
        mock_request.return_value = FakeResponse(ok_payload({'request_id': 'rid-3'}))

        client = Notificator('demo', 'account-token', host='http://localhost:8001')
        client.ntfy(
            'https://ntfy.sh/server-alerts',
            'markdown',
            '**healthy**',
            title='Deploy',
            token='tk_secret',
            priority='high',
            tags=['white_check_mark'],
            click='https://example.com/jobs/42',
        )

        payload = mock_request.call_args.kwargs['json']
        self.assertEqual('markdown', payload['message']['format'])
        self.assertEqual('ntfy', payload['deliveries'][0]['channel'])
        self.assertEqual('https://ntfy.sh/server-alerts', payload['deliveries'][0]['target'])
        self.assertEqual(
            {
                'title': 'Deploy',
                'token': 'tk_secret',
                'priority': 'high',
                'tags': ['white_check_mark'],
                'click': 'https://example.com/jobs/42',
            },
            payload['deliveries'][0]['options'],
        )


if __name__ == '__main__':
    unittest.main()
