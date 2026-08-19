
from notificator import Notificator

notificator = Notificator(
    name="Qitian",
    token="DOnD8ee7ofFVcQWybsSKmywAPjhYJdON",
    host="https://notice.6-79.cn",
)

result = notificator.prepare_mail("liu@qijiong.work").send(
    format="verification",
    body={"code": "482901", "time": 10},
)

print(result)
