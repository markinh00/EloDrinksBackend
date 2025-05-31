from datetime import datetime, timezone, timedelta

UTC_MINUS_3 = timezone(timedelta(hours=-3))


def get_current_time_utc_minus_3():
    """Retorna o horário atual no fuso horário UTC-3."""
    return datetime.now(UTC_MINUS_3)
