from datetime import datetime
from collections import Counter


def pick_date(avalibilities: list) -> datetime or None:
    ok_datetimes, maybe_datetimes, no_datetimes = parse_availibilities(
        avalibilities)
    ok_datetimes = remove_repetitions(ok_datetimes)
    maybe_datetimes = remove_repetitions(maybe_datetimes)
    no_datetimes = remove_repetitions(no_datetimes)
    if ok_datetime := select_datetime(ok_datetimes, no_datetimes):
        return ok_datetime
    if maybe_datetime := select_datetime(maybe_datetimes, no_datetimes):
        return maybe_datetime
    else:
        return None


def select_datetime(datetimes: list, no_datetimes: list) -> datetime:
    distinct_datetimes = remove_repetitions(datetimes)
    filtered_datetimes = [
        dt for dt in distinct_datetimes if dt not in no_datetimes]
    if legit_datetimes := [i for i in datetimes if i in filtered_datetimes]:
        if len(legit_datetimes) > 0:
            try:
                return Counter(legit_datetimes).most_common(1)[0][0]
            except Exception:
                return legit_datetimes[0]
    else:
        return None


def remove_repetitions(datetimes: list) -> list:
    return list(set(datetimes))


def parse_availibilities(availibilities: list) -> (list, list, list):
    ok_datetimes = []
    maybe_datetimes = []
    no_datetimes = []
    for user_dict in availibilities:
        dates_dict = list(user_dict.values())[0]
        for _, availibility_dict in dates_dict.items():
            ok_datetimes.extend(availibility_dict["ok"])
            maybe_datetimes.extend(availibility_dict["maybe"])
            no_datetimes.extend(availibility_dict["no"])
    return ok_datetimes, maybe_datetimes, no_datetimes
