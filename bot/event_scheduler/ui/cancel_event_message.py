import discord

from event_scheduler.api.event_model import EventModel
from event_scheduler import utils


class CancelEventView(discord.ui.View):
    """View for cancelling an event"""

    def __init__(self, user_id: int, bot: discord.Client = None):
        super().__init__()
        self.bot = bot
        self.events = EventModel.get_from_database_by_creator(
            creator_id=user_id, bot=self.bot)
        self.add_item(EventSelect(self.events))


class EventSelect(discord.ui.Select):
    def __init__(self, events):
        super().__init__(placeholder="Select an event to cancel",
                         options=[
                             discord.SelectOption(label=event_label(event), value=i) for i, event in enumerate(events)
                         ], min_values=0, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = self.view.events[int(self.values[0])]
        message_content = utils.error_message(f"Event {event.name} has been canceled")
        if event.status == "confirmed":
            for p in event.get_participants_ids():
                if user := self.view.bot.get_user(p):
                    print(user)
                    await user.send(message_content)
        event.status = "canceled"
        event.save_in_database()
        await interaction.followup.edit_message(interaction.message.id, content=message_content, view=None, embed=None)


def event_label(event: EventModel) -> str:
    match event.status:
        case "created":
            return f"{event.name}: {utils.date_to_str(event.start_date)} - {utils.date_to_str(event.end_date)}"
        case "confirmed":
            return f"{event.name}: {utils.datetime_to_str(event.picked_datetime)}"
        case _:
            return event.name
