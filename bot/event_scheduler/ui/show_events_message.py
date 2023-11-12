import discord
import event_scheduler.utils as utils

from event_scheduler.api.event_model import EventModel


class ShowEventsEmbed(discord.Embed):
    """Embed for showing events"""

    def __init__(self, events: [EventModel], type: str = "created") -> None:
        """Init"""
        super().__init__(title=f"Events {type}", color=discord.Color.pink())
        self.description = f"List of all {type} events"
        match type:
            case "created":
                self.__add_created_events(events)
            case "confirmed":
                self.__add_confirmed_events(events)
            case "canceled":
                self.__add_canceled_events(events)
            case _:
                raise ValueError("Invalid type")

    def __add_created_events(self, events):
        for event in events:
            self.add_field(
                name=event.get_name(),
                value=f"""
                Participants: {event.get_trunc_participants()}
                Tags: {event.get_trunc_tags()}
                Start Date: {utils.date_to_str(event.start_date)}
                End Date: {utils.date_to_str(event.end_date)}""",
                inline=False
            )

    def __add_confirmed_events(self, events):
        for event in events:
            self.add_field(
                name=event.get_name(),
                value=f"""
                Participants: {event.get_trunc_participants()}
                Tags: {event.get_trunc_tags()}
                Date: {utils.datetime_to_str(event.picked_datetime)}
                """,
                inline=False
            )

    def __add_canceled_events(self, events):
        for event in events:
            self.add_field(
                name=event.get_name(),
                value=f"Date: {event.picked_datetime}",
                inline=False
            )
