from event_scheduler.db import get_database


def get_events(user_id: int, status: str, limit: int = 5):
    """Returns all events with specified status"""
    return get_database()["events"].find({"status": status, "creator_id": user_id})
