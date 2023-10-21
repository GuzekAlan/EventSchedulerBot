from datetime import date
from typing import Optional
from discord import Member
from event_scheduler.db import get_database


class EventModel:
    def __init__(self) -> None:
        self.participants: list(Member) = []
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.tags: list(str) = []
        self.start_date: date = None
        self.end_date: date = None
        self.status: str = "created"

    def add_participant(self, participant: str) -> bool:
        if participant not in self.participants:
            self.participants.append(participant)
            return True
        return False

    def add_tags(self, tags: str) -> bool:
        [self.tags.append(tag)
         for tag in tags.split(",") if tag not in self.tags]

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
            map(lambda p: p.nick if p.nick else p.name, self.participants[:limit]))
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
            "status": self.status
        }
        if verbose:
            print(data)
        return collection.insert_one(data).inserted_id
