import discord

from event_scheduler.api.event_model import EventModel
from event_scheduler import utils


class RescheduleEventView(discord.ui.View):
    """View for rescheduling an event"""

    def __init__(self, user_id: int, status: str, bot: discord.Client = None):
        super().__init__()
        self.bot = bot
        self.events = EventModel.get_from_database_by_creator(
            creator_id=user_id, bot=self.bot, status=status)
        self.add_item(EventSelect(self.events))


class EventSelect(discord.ui.Select):
    def __init__(self, events):
        super().__init__(placeholder="Select an event to reschedule",
                         options=[
                             discord.SelectOption(label=event_label(event), value=i) for i, event in enumerate(events)
                         ], min_values=0, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        event = self.view.events[int(self.values[0])]
        event.status = "created"
        event.picked_datetime = None
        event.availibility = []
        event.save_in_database()
        for p in event.participants:
            self.view.bot.dispatch(
                "start_schedule_event",
                event.event_id,
                p.id
            )
        await interaction.response.edit_message(content=utils.information_message(f"Reschedule event {event.name}"), view=None, embed=None)


def event_label(event: EventModel) -> str:
    match event.status:
        case "created":
            return f"{event.name}: {utils.date_to_str(event.start_date)} - {utils.date_to_str(event.end_date)}"
        case "confirmed":
            return f"{event.name}: {utils.datetime_to_str(event.picked_datetime)}"
        case _:
            return event.name
