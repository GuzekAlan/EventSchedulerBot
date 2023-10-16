from datetime import datetime
from typing import Optional
from discord import Member


class EventModel:
    def __init__(self) -> None:
        self.participants: list(Member) = []
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.tags: list(str) = []
        self.start_datetime: datetime = None
        self.end_datetime: datetime = None

    def add_participant(self, participant: str) -> bool:
        if participant not in self.participants:
            self.participants.append(participant)
            return True
        return False

    def add_tag(self, tag: str) -> bool:
        if tag not in self.tags:
            self.tags.append(tag)
            return True
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
            map(lambda p: p.nick if p.nick else p.name, self.participants[:limit]))
        if len(self.participants) > limit:
            return participants_string + "..."
        return participants_string
