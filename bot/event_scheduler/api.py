"""Logic for backend API which is used by the bot."""
from pymongo.database import Database


def add_user(db: Database, user_id: str, **additional_info: dict) -> bool:
    """Adds a user to the database"""
    result = db.users.insert_one({
        "user_id": user_id,
        **additional_info
    })
    if result.acknowledged:
        return True
    return False


def list_users(db: Database) -> list:
    """Returns a list of all users in the database"""
    result = db.users.find()
    if result:
        return list(result)
    return None


def add_event(db: Database, event_name: str, **additional_info: dict) -> bool:
    """Adds an event to the database"""
    result = db.events.insert_one({
        "event_name": event_name,
        **additional_info
    })
    if result.acknowledged:
        return True
    return False


if __name__ == '__main__':
    import bot.event_scheduler.db as db
    db = db.get_database()
    list_users(db)
