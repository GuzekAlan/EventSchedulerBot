import pytest
from event_scheduler import utils

from datetime import datetime


def test_weekday_name():
    assert utils.weekday_name(datetime(2021, 5, 17)) == "Monday"
    assert utils.weekday_name(datetime(2021, 5, 18)) == "Tuesday"


def test_datetime_to_str():
    assert utils.datetime_to_str(
        datetime(2021, 5, 17, 12, 30)) == "17/05/2021 12:30"
    assert utils.datetime_to_str(
        datetime(2000, 1, 1, 0, 0)) == "01/01/2000 00:00"


def test_date_to_str():
    assert utils.date_to_str(
        datetime(2021, 5, 17, 12, 30)) == "17/05/2021"
    assert utils.date_to_str(
        datetime(2000, 1, 1, 0, 0)) == "01/01/2000"


def test_str_to_date():
    assert utils.str_to_date("17/05/2021") == datetime(2021, 5, 17)
    assert utils.str_to_date("01/01/2000") == datetime(2000, 1, 1)
