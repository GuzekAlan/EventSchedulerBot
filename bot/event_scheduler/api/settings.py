from event_scheduler.db import get_database


def upsert_bot_channel_id(guild_id: int, channel_id: int):
    collection = get_database()["config"]
    return collection.update_one({"guild_id": guild_id}, {
        "$set": {"bot_channel_id": channel_id}}, upsert=True).acknowledged


def get_bot_channel_id(guild_id: int):
    collection = get_database()["config"]
    if config := collection.find_one({"guild_id": guild_id}):
        return config["bot_channel_id"]
    return None
