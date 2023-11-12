from datetime import datetime
from typing import Optional
from discord import Member
from discord.ext import commands
from pymongo import DESCENDING
from event_scheduler import utils
from event_scheduler.db import get_database


class EventModel:
    def __init__(self, owner_id: int) -> None:
        self.creator_id: int = owner_id
        self.participants: list(Member) = []
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.tags: list(str) = []
        self.start_date: datetime = None
        self.end_date: datetime = None
        self.status: str = "created"  # created, confirmed, canceled
        self.picked_datetime: Optional[datetime] = None

    def add_participant(self, participant: str) -> bool:
        if participant not in self.participants:
            self.participants.append(participant)
            return True
        return False

    def remove_participant(self, participant_id: str) -> bool:
        participant_id = int(participant_id)
        if any([p.id == participant_id for p in self.participants]):
            self.participants = [
                p for p in self.participants if p.id != participant_id]
            return True
        return False

    def set_tags(self, tags: str) -> bool:
        self.tags = tags.split(",")

    def set_start_date(self, date: str) -> bool:
        try:
            self.start_date = utils.str_to_date(date)
            return True
        except Exception:
            return False

    def set_end_date(self, date: str) -> bool:
        try:
            self.end_date = utils.str_to_date(date)
            return True
        except Exception:
            return False

    def get_name(self) -> str:
        if self.name:
            return self.name
        return ""

    def get_trunc_tags(self, limit=3):
        if len(self.tags) > limit:
            return ",".join(self.tags[:limit]) + "..."
        else:
            return ",".join(self.tags)

    def get_trunc_participants(self, limit=3):
        participants_string = ",".join(
            map(lambda p: p.nick if hasattr(p, "nick") and p.nick else p.name, self.participants[:limit]))
        if len(self.participants) > limit:
            return participants_string + "..."
        return participants_string

    def save_in_database(self, verbose=False):
        collection = get_database()["events"]
        data = {
            "creator_id": self.creator_id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "participants": list(map(lambda p: p.id, self.participants)),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "availibility": [],
        }
        if verbose:
            print(data)
        return collection.insert_one(data).inserted_id


def get_from_database(event_id: int, bot: commands.Bot):
    collection = get_database()["events"]
    if event := collection.find_one({"_id": event_id}):
        return model_from_database_data(event, bot)
    return None


def get_from_database_by_creator(creator_id: int, bot: commands.Bot, limit: int = 5, status: str = "created"):
    collection = get_database()["events"]
    if events := collection.find({"creator_id": creator_id, "status": status}).sort("date", DESCENDING).limit(limit):
        return [model_from_database_data(event, bot) for event in events]
    return None


def model_from_database_data(event, bot: commands.Bot):
    event_model = EventModel(event["owner_id"])
    event_model.name = event["name"]
    event_model.description = event["description"]
    event_model.tags = event["tags"]
    event_model.participants = [bot.get_user(user_id)
                                for user_id in event["participants"]]
    event_model.start_date = event["start_date"]
    event_model.end_date = event["end_date"]
    event_model.status = event["status"]
    event_model.picked_datetime = event["date"] if "date" in event else None
    return event_model
