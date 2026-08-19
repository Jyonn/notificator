# notificator

Python SDK for [Notificator](https://github.com/Jyonn/notificator), focused on:

- sending notifications through one unified API
- preparing multi-channel deliveries in one request
- managing admin login and account CRUD
- managing mail sender configuration

## Installation

```bash
pip install notificator
```

## Quick Start

```python
from notificator import Notificator

client = Notificator(
    name="demo_account",
    token="account_token",
    host="http://127.0.0.1:8000",
)

result = client.mail(
    mail="user@example.com",
    subject="Build finished",
    body="The nightly build is green.",
    recipient_name="Operator",
    action_url="https://example.com/jobs/42",
    action_text="Open job",
)

print(result)
```

## Unified Multi-Channel Sending

You can prepare multiple deliveries and send them together:

```python
from notificator import Notificator

client = Notificator(
    name="demo_account",
    token="account_token",
    host="http://127.0.0.1:8000",
)

result = (
    client
    .clean()
    .prepare_sms(
        "+8613800000000",
        template_param={"scene": "incident"},
    )
    .prepare_mail(
        "user@example.com",
        recipient_name="Operator",
        action_url="https://example.com/incidents/7",
        action_text="View incident",
    )
    .prepare_webhook(
        "https://example.com/hooks/notificator",
        headers={"Authorization": "Bearer your-secret"},
        body={"source": "notificator-sdk"},
    )
    .send(
        format="verification",
        body={"code": "482901", "time": 10},
        title="Incident opened",
    )
)

print(result)
```

## Shortcut Methods

### Mail

```python
client.mail(
    "user@example.com",
    subject="Welcome",
    body="Your account is ready.",
    recipient_name="Tom",
    footer_note="Sent by Notificator",
)
```

### SMS

```python
client.sms(
    "+8613800000000",
    code="123456",
    time=5,
)
```

### Bark

```python
client.bark(
    "https://api.day.app/your-device-key",
    title="Deploy finished",
    body="Production is healthy.",
)
```

### ntfy

Pass the complete topic URL. `token` is optional for public topics.

```python
client.ntfy(
    "https://ntfy.sh/server-alerts",
    format="markdown",
    title="Deploy finished",
    body="Production is **healthy**.",
    token="tk_your-access-token",
    priority="high",
    tags=["white_check_mark"],
    click="https://example.com/jobs/42",
)
```

### Gotify

Pass the Gotify server URL and an application token. A server hosted below a URL
prefix, such as `https://push.example.com/gotify`, is also supported.

```python
client.gotify(
    "https://push.example.com",
    token="A_your-application-token",
    format="markdown",
    title="Deploy finished",
    body="Production is **healthy**.",
    priority=7,
    click="https://example.com/jobs/42",
    big_image_url="https://example.com/status.png",
)
```

### PushDeer

The official server is used by default. Pass `server` when using a self-hosted
PushDeer instance.

```python
client.pushdeer(
    "PDU_your-push-key",
    format="markdown",
    title="Deploy finished",
    body="Production is **healthy**.",
)

client.pushdeer(
    "PDU_your-push-key",
    body="Production is healthy.",
    server="https://push.example.com/pushdeer",
)
```

### Webhook

```python
client.webhook(
    "https://example.com/hooks/notificator",
    headers={"Authorization": "Bearer your-secret"},
    body={"message": "Production is healthy."},
)
```

## AdminClient

`AdminClient` wraps administrator APIs such as login, account CRUD, and mail sender management.

```python
from notificator import AdminClient

admin = AdminClient(
    email="admin@example.com",
    password="your-password",
    host="http://127.0.0.1:8000",
)

accounts = admin.get_accounts()
print(accounts)

account = admin.create_account(
    name="ops_bot",
    nick="Ops Bot",
)
print(account)

sender_client = admin.get_notificator("ops_bot")
sender_client.webhook(
    "https://example.com/hooks/notificator",
    body={"message": "Hello from Notificator"},
)
```

Mail sender management:

```python
admin.create_mail_sender(
    sender_id="PRIMARY",
    email="noreply@example.com",
    password="app-password",
    smtp_server="smtp.example.com",
    smtp_port=465,
    enabled=True,
    weight=3,
)
```

## Defaults

- default host: `https://notice.6-79.cn`
- default locale: `zh-CN`
- default timeout: `15` seconds

## Errors

The SDK raises:

- `NotificatorError` for client-side validation or request failures
- `NotificatorAPIError` for structured API errors returned by the server

Example:

```python
from notificator import NotificatorAPIError

try:
    client.sms("+8613800000000", code="123456", time=5)
except NotificatorAPIError as err:
    print(err.identifier)
    print(err.message)
    print(err.details)
```

## Testing

Run unit tests:

```bash
python -m unittest tests/test_sdk_unit.py
```

Run integration tests with environment variables:

```bash
export NOTIFICATOR_TEST_HOST=http://127.0.0.1:8000
export NOTIFICATOR_TEST_ADMIN_EMAIL=admin@example.com
export NOTIFICATOR_TEST_ADMIN_PASSWORD=your-password
python -m unittest tests/test_integration.py
```
