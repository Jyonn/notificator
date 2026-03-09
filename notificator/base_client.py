from __future__ import annotations

from typing import Any, Optional

import requests

from notificator.constants import DEFAULT_HOST, DEFAULT_TIMEOUT
from notificator.errors import NotificatorAPIError, NotificatorError


class BaseClient:
    def __init__(
        self,
        host: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.host = (host or DEFAULT_HOST).rstrip('/')
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        route = path if path.startswith('/') else f'/{path}'
        try:
            response = requests.request(
                method=method.upper(),
                url=f'{self.host}{route}',
                json=json_body,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as err:
            raise NotificatorError(f'Request failed: {err}') from err

        try:
            payload = response.json()
        except ValueError as err:
            raise NotificatorError(
                f'Invalid JSON response: status={response.status_code}, text={response.text}'
            ) from err

        if not isinstance(payload, dict):
            raise NotificatorError(f'Invalid response payload type: {type(payload).__name__}')

        identifier = payload.get('identifier')
        if identifier == 'OK':
            return payload.get('body')

        message = payload.get('message', 'Request failed')
        details = payload.get('details', [])
        raise NotificatorAPIError(
            identifier=str(identifier or 'UNKNOWN'),
            message=str(message),
            details=details,
        )
