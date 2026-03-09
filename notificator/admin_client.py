from __future__ import annotations

from typing import Optional, Any

from notificator.base_client import BaseClient
from notificator.constants import DEFAULT_LOCALE, DEFAULT_TIMEOUT
from notificator.errors import NotificatorError
from notificator.notificator import Notificator


class AdminClient(BaseClient):
    def __init__(
        self,
        email: str,
        password: str,
        host: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        auto_login: bool = True,
    ):
        super().__init__(host=host, timeout=timeout)
        self.email = email
        self.password = password
        self.token: Optional[str] = None

        if auto_login:
            self.login()

    def login(
        self,
        store: bool = True,
    ):
        data = self._request(
            'POST',
            '/api/auth',
            json_body={'email': self.email, 'password': self.password},
        )
        if store and isinstance(data, dict) and data.get('token'):
            self.token = data['token']
        return data

    def admin_request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: Optional[dict] = None,
        token: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        admin_token = token or self.token
        if not admin_token:
            raise NotificatorError('Missing admin token. Call login() first or pass token.')

        req_headers = {'Token': admin_token}
        if headers:
            req_headers.update(headers)

        return self._request(
            method,
            path,
            json_body=json_body,
            params=params,
            headers=req_headers,
        )

    def get_accounts(self, token: Optional[str] = None):
        return self.admin_request('GET', '/api/account/', token=token)

    def create_account(
        self,
        name: str,
        nick: str,
        token: Optional[str] = None,
    ):
        return self.admin_request(
            'POST',
            '/api/account/',
            json_body={'name': name, 'nick': nick},
            token=token,
        )

    def update_account(
        self,
        account_id: int,
        *,
        name: Optional[str] = None,
        nick: Optional[str] = None,
        renew_token: bool = False,
        token: Optional[str] = None,
    ):
        return self.admin_request(
            'PUT',
            '/api/account/',
            params={'id': account_id},
            json_body={
                'name': name,
                'nick': nick,
                'renew': bool(renew_token),
            },
            token=token,
        )

    def delete_account(self, account_id: int, token: Optional[str] = None):
        return self.admin_request(
            'DELETE',
            '/api/account/',
            params={'id': account_id},
            token=token,
        )

    def get_account(self, account_name: str, token: Optional[str] = None):
        accounts = self.get_accounts(token=token)
        if not isinstance(accounts, list):
            raise NotificatorError('Account list response is not a list.')

        for account in accounts:
            if isinstance(account, dict) and account.get('name') == account_name:
                return account
        raise NotificatorError(f'Account not found: {account_name}')

    def get_notificator(
        self,
        account_name: str,
        *,
        locale: str = DEFAULT_LOCALE,
        timeout: Optional[int] = None,
        token: Optional[str] = None,
    ) -> Notificator:
        account = self.get_account(account_name, token=token)
        name = account.get('name')
        account_token = account.get('token')
        if not name or not account_token:
            raise NotificatorError(f'Account token is missing for account: {account_name}')

        return Notificator(
            name=name,
            token=account_token,
            host=self.host,
            timeout=timeout or self.timeout,
            locale=locale,
        )

    def get_mail_senders(self, token: Optional[str] = None):
        return self.admin_request('GET', '/api/channel/mail', token=token)

    def get_mail_sender(self, sender_id: str, token: Optional[str] = None):
        return self.admin_request('GET', f'/api/channel/mail/{sender_id}', token=token)

    def create_mail_sender(
        self,
        sender_id: str,
        email: str,
        password: str,
        smtp_server: str,
        smtp_port: int,
        *,
        enabled: bool = True,
        weight: int = 1,
        token: Optional[str] = None,
    ):
        return self.admin_request(
            'POST',
            '/api/channel/mail',
            json_body={
                'sender_id': sender_id,
                'email': email,
                'password': password,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'enabled': enabled,
                'weight': weight,
            },
            token=token,
        )

    def update_mail_sender(
        self,
        sender_id: str,
        *,
        email: Optional[str] = None,
        password: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        enabled: Optional[bool] = None,
        weight: Optional[int] = None,
        token: Optional[str] = None,
    ):
        payload = {
            'email': email,
            'password': password,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'enabled': enabled,
            'weight': weight,
        }
        final_payload = {key: value for key, value in payload.items() if value is not None}

        return self.admin_request(
            'PUT',
            f'/api/channel/mail/{sender_id}',
            json_body=final_payload,
            token=token,
        )

    def delete_mail_sender(self, sender_id: str, token: Optional[str] = None):
        return self.admin_request('DELETE', f'/api/channel/mail/{sender_id}', token=token)
