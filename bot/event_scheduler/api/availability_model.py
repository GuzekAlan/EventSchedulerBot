from datetime import time, datetime, timedelta
from event_scheduler import utils
from event_scheduler.db import get_database
from bson.objectid import ObjectId


class AvailabilityModel:
    times = [time(hour=hour) for hour in range(24)]

    def __init__(self, event_id: int, user_id: int, start_date: datetime, end_date: datetime) -> None:
        self.current_date = start_date
        self.start_date = start_date
        self.end_date = end_date
        self.event_id = event_id
        self.user_id = user_id
        self.availability = {
            utils.date_to_str(start_date + timedelta(days=i)): {"ok": [], "maybe": [], "no": []} for i in range((end_date - start_date).days + 1)
        }
        self.not_available_datetimes = self.get_user_not_available_datetimes()

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

    def add_times(self, times: list, availability: str = "maybe") -> bool:
        if availability not in ["ok", "maybe", "no"]:
            return False
        self.availability[utils.date_to_str(
            self.current_date)][availability] = [datetime.combine(self.current_date.date(), time) for time in times]
        return True

    def is_time_checked(self, time: time, availability: str = "maybe") -> bool:
        if availability not in ["ok", "maybe", "no"]:
            return False
        chosen_hour = time.hour
        selected_hours = [time.hour for time in self.availability[utils.date_to_str(
            self.current_date)][availability]]
        return chosen_hour in selected_hours

    def is_time_available(self, time: time) -> bool:
        return datetime.combine(self.current_date.date(), time) not in self.not_available_datetimes

    def save_in_database(self):
        for date in self.availability.keys():
            ok_times = [dt.time() for dt in self.availability[date]["ok"]]
            maybe_times = [dt.time()
                           for dt in self.availability[date]["maybe"]]
            self.availability[date]["no"] = [
                datetime.combine(utils.str_to_date(date), time) for time in self.times if time not in ok_times and time not in maybe_times
            ]
        collection = get_database()["events"]
        data = {
            str(self.user_id): self.availability
        }
        updated = collection.update_one({"_id": ObjectId(self.event_id)}, {
            "$push": {"availability": data}})
        print(f"UPDATED: {updated}")
        return updated.acknowledged

    def get_user_not_available_datetimes(self):
        if user := get_database()["users"].find_one({"user_id": self.user_id}):
            return [e["date"] for e in user["events"]]
        return None
