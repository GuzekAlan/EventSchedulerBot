"""Utils module for the bot"""
from datetime import datetime


def users_list(users: list, sep: str = ',') -> str:
    """Returns a comma separated list of users"""
    return sep.join([user['user_id'] for user in users])


def weekday_name(date: datetime) -> str:
    """Returns the name of the weekday"""
    weekdays = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = date.weekday()
    if weekday < 0 or weekday > 6:
        return None
    return weekdays[weekday]


def datetime_to_str(datetime: datetime) -> str:
    return datetime.strftime("%d/%m/%Y %H:%M")


def date_to_str(date: datetime) -> str:
    return date.strftime("%d/%m/%Y")


def str_to_date(date: str) -> datetime:
    return datetime.strptime(date, '%d/%m/%Y')


def information_message(text):
    return f"```ansi\n\u001b[36m{text}\n```"


def error_message(text):
    return f"```ansi\n\u001b[31m{text}\n```"
