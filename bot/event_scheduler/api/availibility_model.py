from datetime import time, datetime, timedelta
from event_scheduler import utils
from event_scheduler.db import get_database


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

    def is_time_checked(self, time: time, availibility: str = "maybe") -> bool:
        if availibility not in ["ok", "maybe", "no"]:
            return False
        chosen_hour = time.hour
        selected_hours = [time.hour for time in self.availibility[utils.date_to_str(
            self.current_date)][availibility]]
        return chosen_hour in selected_hours

    def save_in_database(self):
        for date in self.availibility.keys():
            ok_times = [dt.time() for dt in self.availibility[date]["ok"]]
            maybe_times = [dt.time()
                           for dt in self.availibility[date]["maybe"]]
            self.availibility[date]["no"] = [
                datetime.combine(utils.str_to_date(date), time) for time in self.times if time not in ok_times and time not in maybe_times
            ]
        collection = get_database()["events"]
        data = {
            str(self.user_id): self.availibility
        }
        return collection.update_one({"_id": self.event_id}, {
            "$push": {"availibility": data}}).acknowledged
