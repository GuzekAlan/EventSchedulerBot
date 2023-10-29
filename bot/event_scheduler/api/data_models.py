from datetime import datetime, timedelta, time
from typing import Optional
from discord import Member
from discord.ext import commands
from event_scheduler.db import get_database
import event_scheduler.utils as utils


class EventModel:
    def __init__(self) -> None:
        self.participants: list(Member) = []
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.tags: list(str) = []
        self.start_date: datetime = None
        self.end_date: datetime = None
        self.status: str = "created"
        self.picked_datetime: Optional[datetime] = None

    def add_participant(self, participant: str) -> bool:
        if participant not in self.participants:
            self.participants.append(participant)
            return True
        return False

    def add_tags(self, tags: str) -> bool:
        [self.tags.append(tag)
         for tag in tags.split(",") if tag not in self.tags]

    def add_start_date(self, date: str) -> bool:
        try:
            self.start_date = utils.str_to_date(date)
            return True
        except:
            return False

    def add_end_date(self, date: str) -> bool:
        try:
            self.end_date = utils.str_to_date(date)
            return True
        except:
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


class FilledEventModel(EventModel):
    def __init__(self, event_id: int, bot: commands.Bot) -> None:
        super().__init__()
        self.event_id = event_id
        self.load_from_database(bot)

    def load_from_database(self, bot: commands.Bot):
        collection = get_database()["events"]
        if event := collection.find_one({"_id": self.event_id}):
            self.name = event["name"]
            self.description = event["description"]
            self.tags = event["tags"]
            self.participants = [bot.get_user(user_id)
                                 for user_id in event["participants"]]
            self.start_date = event["start_date"]
            self.end_date = event["end_date"]
            self.status = event["status"]
            self.picked_datetime = event["date"] if "date" in event else None


class AvailibilityModel:
    times = [time(hour=hour) for hour in range(24)]

    def __init__(self, event_id: int, user_id: int, start_date: datetime, end_date: datetime) -> None:
        self.current_date = start_date
        self.start_date = start_date
        self.end_date = end_date
        self.event_id = event_id
        self.user_id = user_id
        self.availibility = {
            utils.date_to_str(start_date + timedelta(days=i)): {"ok": [], "maybe": [], "no": []} for i in range((end_date - start_date).days)
        }

    def change_day(self, direction: str, days: int = 1) -> bool:
        new_date = self.current_date
        if direction == "next":
            new_date = self.current_date + timedelta(days=days)
        elif direction == "previous":
            new_date = self.current_date - timedelta(days=days)
        else:
            return False
        if new_date >= self.start_date and new_date <= self.end_date:
            self.current_date = new_date
        return True

    def add_times(self, times: list, availibility: str = "maybe") -> bool:
        if availibility not in ["ok", "maybe", "no"]:
            return False
        self.availibility[utils.date_to_str(
            self.current_date)][availibility] = [datetime.combine(self.current_date.date(), time) for time in times]
        return True

    def save_in_database(self):
        collection = get_database()["events"]
        data = {
            str(self.user_id): self.availibility
        }
        return collection.update_one({"_id": self.event_id}, {
            "$push": {"availibility": data}}).acknowledged
