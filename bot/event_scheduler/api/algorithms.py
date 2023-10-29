from datetime import datetime, timedelta


def pick_date(avalibilities: list()) -> datetime:
    # TODO: Implement real algorithm
    return datetime.now() + timedelta(days=1)
