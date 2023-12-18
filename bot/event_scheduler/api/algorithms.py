import math

from datetime import datetime, timedelta
from collections import Counter


def pick_date(availabilities: list, duration: int) -> datetime or None:
    full_additional_duration_hours = math.ceil(max(0, duration-60) / 60)
    ok_datetimes, maybe_datetimes, no_datetimes = parse_availabilities(
        availabilities)
    no_datetimes = add_duration_to_no_times(
        no_datetimes, full_additional_duration_hours)
    if ok_datetime := select_datetime(ok_datetimes, no_datetimes):
        return ok_datetime
    if maybe_datetime := select_datetime(ok_datetimes + maybe_datetimes, no_datetimes):
        return maybe_datetime
    else:
        return None


def add_duration_to_no_times(no_datetimes: list, duration: int) -> list:
    new_no_datetimes = no_datetimes.copy()
    for i in range(duration):
        for dt in no_datetimes:
            new_no_datetimes.append(dt - timedelta(hours=i))
    return new_no_datetimes


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
    else:
        return None


def remove_repetitions(datetimes: list) -> list:
    return list(set(datetimes))


def parse_availabilities(availabilities: list) -> (list, list, list):
    ok_datetimes = []
    maybe_datetimes = []
    no_datetimes = []
    for user_dict in availabilities:
        dates_dict = list(user_dict.values())[0]
        for _, availability_dict in dates_dict.items():
            ok_datetimes.extend(availability_dict["ok"])
            maybe_datetimes.extend(availability_dict["maybe"])
            no_datetimes.extend(availability_dict["no"])
    return ok_datetimes, maybe_datetimes, no_datetimes
