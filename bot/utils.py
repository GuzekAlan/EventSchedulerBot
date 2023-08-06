"""Utils module for the bot"""

def users_list(users: list, sep: str = ',') -> str:
    """Returns a comma separated list of users"""
    return sep.join([user['user_id'] for user in users])