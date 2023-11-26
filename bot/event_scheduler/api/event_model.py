from datetime import datetime
from typing import Optional
from discord import Member
from discord.ext import commands
from pymongo import DESCENDING
from event_scheduler.api.algorithms import pick_date
from event_scheduler import utils
from event_scheduler.db import get_database
from bson.objectid import ObjectId


class EventModel:
    def __init__(self, creator_id: int, guild_id: int) -> None:
        self.event_id: int = None
        self.creator_id: int = creator_id
        self.guild_id: int = guild_id
        self.participants: list(Member) = []
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.duration: int = None
        self.start_date: datetime = None
        self.end_date: datetime = None
        self.status: str = "created"  # created, confirmed, canceled
        self.availibility: list = []
        self.picked_datetime: Optional[datetime] = None

    def get_participants_ids(self) -> [int]:
        return [p.id for p in self.participants]

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

    def get_trunc_participants(self, limit=3):
        participants_string = ",".join(
            map(lambda p: p.nick if hasattr(p, "nick") and p.nick else p.name, self.participants[:limit]))
        if len(self.participants) > limit:
            return participants_string + "..."
        return participants_string

    def save_in_database(self, verbose=False) -> int:
        collection = get_database()["events"]
        data = {
            "creator_id": self.creator_id,
            "guild_id": self.guild_id,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "participants": list(map(lambda p: p.id, self.participants)),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "availibility": self.availibility,
            "date": self.picked_datetime
        }
        if verbose:
            print(data)
        if self.event_id:
            collection.update_one({"_id": self.event_id}, {
                "$set": data})
        else:
            self.event_id = collection.insert_one(data).inserted_id
        return self.event_id

    def not_answered(self) -> int:
        return len(self.participants) - len(self.availibility)

    def choose_date(self) -> str:
        date = pick_date(self.availibility, duration=int(self.duration))
        if date:
            self.picked_datetime = date
            if not get_database()["events"].update_one({"_id": self.event_id}, {
                    "$set": {"status": "confirmed", "date": date}}).acknowledged:
                return "Error while saving event to databse"
            for user_id in self.get_participants_ids():
                data = {
                    "_id": self.event_id,
                    "creator_id": self.creator_id,
                    "guild_id": self.guild_id,
                    "name": self.name,
                    "description": self.description,
                    "duration": self.duration,
                    "participants": list(map(lambda p: p.id, self.participants)),
                    "status": self.status,
                    "date": self.picked_datetime
                }
                if not get_database()["users"].update_one({"user_id": user_id}, {
                        "$push": {"events": data}}, upsert=True).acknowledged:
                    return "Error while updating user in database"
            return None
        return f"No date picked for event {self.name}"

    def get_from_database(event_id: str, bot: commands.Bot, status: str = None):
        collection = get_database()["events"]
        filter = {"_id": ObjectId(event_id), "status": status} if status else {
            "_id": ObjectId(event_id)}
        if event := collection.find_one(filter):
            return model_from_database_data(event, bot)
        return None

    def get_from_database_by_creator(creator_id: int, bot: commands.Bot, limit: int = 0, status: str = "created"):
        collection = get_database()["events"]
        if events := collection.find({"creator_id": creator_id, "status": status}).sort("date", DESCENDING).limit(limit):
            return [model_from_database_data(event, bot) for event in events]
        return None


def model_from_database_data(event, bot: commands.Bot):
    event_model = EventModel(event["creator_id"], event["guild_id"])
    event_model.event_id = event["_id"]
    event_model.name = event["name"]
    event_model.description = event["description"]
    event_model.duration = event["duration"]
    event_model.participants = [bot.get_user(user_id)
                                for user_id in event["participants"]]
    event_model.start_date = event["start_date"]
    event_model.end_date = event["end_date"]
    event_model.status = event["status"]
    event_model.availibility = event["availibility"]
    event_model.picked_datetime = event["date"] if "date" in event else None
    return event_model
