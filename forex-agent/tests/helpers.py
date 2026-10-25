from datetime import datetime, timedelta, timezone

from fxagent.models import Candle

T0 = datetime(2024, 1, 1, tzinfo=timezone.utc)


def bar(i, o, h, l, c):
    return Candle(T0 + timedelta(hours=i), o, h, l, c)


def flat(n, price=1.1, start=0):
    return [bar(start + i, price, price + 0.0001, price - 0.0001, price) for i in range(n)]
