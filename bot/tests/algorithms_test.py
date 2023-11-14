import pytest
from event_scheduler.api import algorithms
from datetime import datetime, time, date

patterns = {
    'user1': ['ok', 'no', 'ok', 'no', 'ok', 'maybe', 'no', 'maybe', 'no'],
    'user2': ['no', 'no', 'no', 'ok', 'ok', 'maybe', 'no', 'maybe', 'no'],
    'user3': ['ok', 'no', 'ok', 'no', 'ok', 'maybe', 'no', 'ok', 'no']
}


@pytest.fixture
def example_availability():
    users = ['user1', 'user2', 'user3']
    dates = [date(2023, 11, i) for i in range(12, 15)]
    hours = [time(hour=i) for i in range(0, 3)]
    dts = [datetime.combine(date, hour)
           for date in dates for hour in hours]

    def datetimes(user, n, status):
        datetimes = []
        for i, v in enumerate(patterns[user][n*3:n*3+3]):
            if v == status:
                datetimes.append(dts[n*3+i])
        return datetimes

    return [
        {user: {
            d.strftime("%d/%m/%Y"): {
                'ok': datetimes(user, n, 'ok'),
                'maybe': datetimes(user, n, 'maybe'),
                'no': datetimes(user, n, 'no')
            } for n, d in enumerate(dates)}

         } for user in users
    ]


def test_parse_availibilities(example_availability):
    ok_datetimes, maybe_datetimes, no_datetimes = algorithms.parse_availibilities(
        example_availability)
    ok_count = sum([pattern.count('ok') for pattern in [
                   patterns['user1'], patterns['user2'], patterns['user3']]])
    maybe_count = sum([pattern.count('maybe') for pattern in [
                      patterns['user1'], patterns['user2'], patterns['user3']]])
    no_count = sum([pattern.count('no') for pattern in [
                   patterns['user1'], patterns['user2'], patterns['user3']]])

    assert len(ok_datetimes) == ok_count
    assert len(maybe_datetimes) == maybe_count
    assert len(no_datetimes) == no_count


def test_remove_repetitions():
    assert algorithms.remove_repetitions([1, 1, 2, 2, 3, 3]) == [1, 2, 3]


def test_select_datetime_ok_datetimes(example_availability):
    ok_datetimes, _, no_datetimes = algorithms.parse_availibilities(
        example_availability)
    assert algorithms.select_datetime(
        ok_datetimes, no_datetimes) == datetime(2023, 11, 13, 1)


def test_select_datetime_maybe_datetimes(example_availability):
    _, maybe_datetimes, no_datetimes = algorithms.parse_availibilities(
        example_availability)
    assert algorithms.select_datetime(
        maybe_datetimes, no_datetimes) == datetime(2023, 11, 13, 2)


def test_pick_datetime(example_availability):
    assert algorithms.pick_date(
        example_availability, 60) == datetime(2023, 11, 13, 1)
