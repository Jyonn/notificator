from __future__ import annotations

from typing import Any, List, Optional

from notificator.base_client import BaseClient
from notificator.constants import DEFAULT_LOCALE, DEFAULT_TIMEOUT
from notificator.errors import NotificatorError


class Notificator(BaseClient):
    MESSAGE_FORMATS = {'text', 'html', 'markdown', 'json', 'verification'}

    def __init__(
        self,
        name: str,
        token: str,
        host: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        locale: str = DEFAULT_LOCALE,
    ):
        super().__init__(host=host, timeout=timeout)

        if not isinstance(name, str) or not name.strip():
            raise NotificatorError('name is required.')
        if not isinstance(token, str) or not token.strip():
            raise NotificatorError('token is required.')

        self.name = name.strip()
        self.token = token.strip()
        self.auth = self.build_auth(self.name, self.token)
        self.locale = locale

        self._prepared_deliveries: List[dict] = []

    @staticmethod
    def build_auth(name: str, token: str) -> str:
        return f'{name}${token}'

    @staticmethod
    def _drop_none(data: dict) -> dict:
        return {key: value for key, value in data.items() if value is not None}

    def _normalize_shortcut_message(self, format: Any, body: Any) -> tuple[str, Any]:
        if body is None and isinstance(format, str) and format not in self.MESSAGE_FORMATS:
            return 'text', format
        return str(format or 'text'), body

    def _build_message(
        self,
        *,
        format: str,
        body: Any,
        title: Optional[str] = None,
        locale: Optional[str] = None,
        code: Optional[str] = None,
        time: Optional[int] = None,
    ) -> dict:
        message_body = body
        if format == 'verification':
            if message_body is None:
                message_body = {'code': code, 'time': time}
            if not isinstance(message_body, dict):
                raise NotificatorError('verification format requires body=dict(code,time).')

        if message_body is None:
            raise NotificatorError('Message body is required.')

        message = {
            'format': format,
            'body': message_body,
        }
        if title is not None:
            message['title'] = title

        final_locale = locale or self.locale
        if final_locale is not None:
            message['locale'] = final_locale
        return message

    def clean(self) -> 'Notificator':
        self._prepared_deliveries = []
        return self

    def prepare_delivery(self, channel: str, target: str, options: Optional[dict] = None) -> 'Notificator':
        self._prepared_deliveries.append(
            {
                'channel': channel,
                'target': target,
                'options': self._drop_none(dict(options or {})),
            }
        )
        return self

    def prepare_bark(
        self,
        uri: str,
        *,
        sound: Optional[str] = None,
        icon: Optional[str] = None,
        group: Optional[str] = None,
        url: Optional[str] = None,
        title: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'title': title,
            'sound': sound,
            'icon': icon,
            'group': group,
            'url': url,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('bark', uri, payload)

    def prepare_sms(
        self,
        phone: str,
        *,
        template_param: Optional[dict] = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'template_param': template_param,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('sms', phone, payload)

    def prepare_ntfy(
        self,
        uri: str,
        *,
        token: Optional[str] = None,
        priority: Optional[Any] = None,
        tags: Optional[List[str]] = None,
        click: Optional[str] = None,
        icon: Optional[str] = None,
        title: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'title': title,
            'token': token,
            'priority': priority,
            'tags': tags,
            'click': click,
            'icon': icon,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('ntfy', uri, payload)

    def prepare_gotify(
        self,
        uri: str,
        *,
        token: str,
        priority: Optional[int] = None,
        click: Optional[str] = None,
        big_image_url: Optional[str] = None,
        extras: Optional[dict] = None,
        title: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'title': title,
            'token': token,
            'priority': priority,
            'click': click,
            'big_image_url': big_image_url,
            'extras': extras,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('gotify', uri, payload)

    def prepare_pushdeer(
        self,
        pushkey: str,
        *,
        server: Optional[str] = None,
        title: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'title': title,
            'server': server,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('pushdeer', pushkey, payload)

    def prepare_mail(
        self,
        mail: str,
        *,
        recipient_name: Optional[str] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        footer_note: Optional[str] = None,
        locale: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'recipient_name': recipient_name,
            'action_url': action_url,
            'action_text': action_text,
            'footer_note': footer_note,
            'locale': locale,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('mail', mail, payload)

    def prepare_webhook(
        self,
        url: str,
        *,
        method: Optional[str] = None,
        headers: Optional[dict] = None,
        query: Optional[dict] = None,
        body: Any = None,
        options: Optional[dict] = None,
    ) -> 'Notificator':
        payload = {
            'method': method,
            'headers': headers,
            'query': query,
            'body': body,
        }
        if options:
            payload.update(options)
        return self.prepare_delivery('webhook', url, payload)

    def send(
        self,
        format: str = 'text',
        body: Any = None,
        title: Optional[str] = None,
        locale: Optional[str] = None,
        code: Optional[str] = None,
        time: Optional[int] = None,
        message: Optional[dict] = None,
        deliveries: Optional[List[dict]] = None,
    ):
        final_message = dict(message) if isinstance(message, dict) else self._build_message(
            format=format,
            body=body,
            title=title,
            locale=locale,
            code=code,
            time=time,
        )

        final_deliveries: List[dict] = []
        if self._prepared_deliveries:
            final_deliveries.extend(self._prepared_deliveries)
        if deliveries:
            final_deliveries.extend(deliveries)

        if not final_deliveries:
            raise NotificatorError('No deliveries prepared. Use prepare_*() or pass deliveries.')

        payload = {
            'message': final_message,
            'deliveries': final_deliveries,
        }

        response = self._request(
            'POST',
            '/api/channel/send',
            json_body=payload,
            headers={
                'Auth': self.auth,
            },
        )

        self.clean()
        return response

    def bark(
        self,
        uri: str,
        format: str = 'text',
        body: Any = None,
        title: Optional[str] = None,
        *,
        locale: Optional[str] = None,
        sound: Optional[str] = None,
        icon: Optional[str] = None,
        group: Optional[str] = None,
        url: Optional[str] = None,
        options: Optional[dict] = None,
    ):
        format, body = self._normalize_shortcut_message(format, body)
        return self.clean().prepare_bark(
            uri,
            title=title,
            sound=sound,
            icon=icon,
            group=group,
            url=url,
            options=options,
        ).send(
            format=format,
            body=body,
            title=title,
            locale=locale,
        )

    def sms(
        self,
        phone: str,
        format: str = 'verification',
        body: Any = None,
        title: Optional[str] = None,
        *,
        locale: Optional[str] = None,
        template_param: Optional[dict] = None,
        code: Optional[str] = None,
        time: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        # Backward compatibility: sms(phone, code, time)
        if format not in self.MESSAGE_FORMATS:
            code = str(format)
            if isinstance(body, int):
                time = body
                body = None
            format = 'verification'

        if format == 'verification' and body is None:
            body = {
                'code': code,
                'time': time,
            }

        return self.clean().prepare_sms(
            phone,
            template_param=template_param,
            options=options,
        ).send(
            format=format,
            body=body,
            title=title,
            locale=locale,
        )

    def ntfy(
        self,
        uri: str,
        format: str = 'text',
        body: Any = None,
        title: Optional[str] = None,
        *,
        locale: Optional[str] = None,
        token: Optional[str] = None,
        priority: Optional[Any] = None,
        tags: Optional[List[str]] = None,
        click: Optional[str] = None,
        icon: Optional[str] = None,
        options: Optional[dict] = None,
    ):
        format, body = self._normalize_shortcut_message(format, body)
        return self.clean().prepare_ntfy(
            uri,
            title=title,
            token=token,
            priority=priority,
            tags=tags,
            click=click,
            icon=icon,
            options=options,
        ).send(
            format=format,
            body=body,
            title=title,
            locale=locale,
        )

    def gotify(
        self,
        uri: str,
        token: str,
        format: str = 'text',
        body: Any = None,
        title: Optional[str] = None,
        *,
        locale: Optional[str] = None,
        priority: Optional[int] = None,
        click: Optional[str] = None,
        big_image_url: Optional[str] = None,
        extras: Optional[dict] = None,
        options: Optional[dict] = None,
    ):
        format, body = self._normalize_shortcut_message(format, body)
        return self.clean().prepare_gotify(
            uri,
            title=title,
            token=token,
            priority=priority,
            click=click,
            big_image_url=big_image_url,
            extras=extras,
            options=options,
        ).send(
            format=format,
            body=body,
            title=title,
            locale=locale,
        )

    def pushdeer(
        self,
        pushkey: str,
        format: str = 'text',
        body: Any = None,
        title: Optional[str] = None,
        *,
        locale: Optional[str] = None,
        server: Optional[str] = None,
        options: Optional[dict] = None,
    ):
        format, body = self._normalize_shortcut_message(format, body)
        return self.clean().prepare_pushdeer(
            pushkey,
            title=title,
            server=server,
            options=options,
        ).send(
            format=format,
            body=body,
            title=title,
            locale=locale,
        )

    def mail(
        self,
        mail: str,
        format: str = 'text',
        body: Any = None,
        title: Optional[str] = None,
        *,
        subject: Optional[str] = None,
        locale: Optional[str] = None,
        recipient_name: Optional[str] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        footer_note: Optional[str] = None,
        options: Optional[dict] = None,
    ):
        format, body = self._normalize_shortcut_message(format, body)
        final_title = title or subject
        return self.clean().prepare_mail(
            mail,
            recipient_name=recipient_name,
            action_url=action_url,
            action_text=action_text,
            footer_note=footer_note,
            locale=locale,
            options=options,
        ).send(
            format=format,
            body=body,
            title=final_title,
            locale=locale,
        )

    def webhook(
        self,
        url: str,
        format: Optional[str] = None,
        body: Any = None,
        title: Optional[str] = None,
        *,
        locale: Optional[str] = None,
        method: Optional[str] = 'POST',
        headers: Optional[dict] = None,
        query: Optional[dict] = None,
        options: Optional[dict] = None,
    ):
        if body is None and isinstance(format, str) and format not in self.MESSAGE_FORMATS:
            body = format
            format = None

        final_format = format
        if not final_format:
            final_format = 'json' if isinstance(body, (dict, list)) else 'text'

        return self.clean().prepare_webhook(
            url,
            method=method,
            headers=headers,
            query=query,
            body=body,
            options=options,
        ).send(
            format=final_format,
            body=body,
            title=title,
            locale=locale,
        )
