import discord
import re
from discord import ui
from discord.interactions import Interaction
from event_scheduler import utils
from event_scheduler.api.event_model import EventModel
from datetime import datetime, timedelta


class ScheduleEventEmbed(discord.Embed):
    def __init__(self, model: EventModel, title: str = "Schedule Event"):
        super().__init__(title=title, color=discord.Color.pink())
        self.model = model

    def reload_embed(self):
        self.clear_fields()
        if self.model.picked_datetime:
            self.add_field(name="Date",
                           value=utils.datetime_to_str(self.model.picked_datetime), inline=False)
        self.add_field(name="Event Name",
                       value=self.model.name, inline=False)
        if self.model.description:
            self.add_field(name="Description",
                           value=self.model.description, inline=False)
        if self.model.duration:
            self.add_field(name="Duration",
                           value=f"{self.model.duration} minutes", inline=False)
        self.add_field(
            name="Participants", value=self.model.get_trunc_participants(), inline=False)
        return self


class ScheduleEventView(ui.View):
    """View for scheduling an event"""

    def __init__(self, model: EventModel, bot: discord.Client = None):
        super().__init__()
        self.bot = bot
        self.embed = ScheduleEventEmbed(model=model)
        self.embed = self.embed.reload_embed()
        self.add_participant_button = AddParticipantButton(self.embed)
        self.add_item(self.add_participant_button)
        self.remove_participant_button = RemoveParticipantButton(self.embed)
        self.add_item(self.remove_participant_button)
        self.add_description_button = AddDescriptionButton(self.embed)
        self.add_item(self.add_description_button)
        self.save_button = SaveButton(self.embed)
        self.add_item(self.save_button)
        self.add_item(CancelButton(self.embed))

# Buttons


class AddParticipantButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Add Participant", style=discord.ButtonStyle.primary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.add_item(AddParticipantSelect(self.embed))
        self.style = discord.ButtonStyle.secondary
        self.disabled = True
        await interaction.response.edit_message(view=self.view)


class RemoveParticipantButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Remove Participant", style=discord.ButtonStyle.secondary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.add_item(RemoveParticipantSelect(self.embed))
        self.disabled = True
        await interaction.response.edit_message(view=self.view)


class AddDescriptionButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Add Info", style=discord.ButtonStyle.primary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(AddDescriptionModal(self.view, self.embed))


class CancelButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(content=utils.error_message("Scheduling an event has been canceled"), view=None, embed=None)


class SaveButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Save", style=discord.ButtonStyle.green, disabled=True)
        self.is_participant_added = False
        self.is_info_added = False
        self.embed = embed

    def maybe_able(self):
        if self.is_participant_added and self.is_info_added:
            self.disabled = False

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        if event_id := self.embed.model.save_in_database():
            for p in self.embed.model.participants:
                self.view.bot.dispatch(
                    "start_schedule_event",
                    event_id,
                    p.id
                )
            await interaction.followup.edit_message(interaction.message.id, content="Event created!", embed=None, view=None)
        else:
            await interaction.followup.send_message(interaction.message.id, content=utils.error_message("Ups, something went wrong!"))


# UI Objects


class AddParticipantSelect(ui.UserSelect):
    def __init__(self, embed):
        super().__init__(placeholder="Select a participant to add", min_values=0, max_values=1)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.remove_item(self)
        self.view.add_participant_button.disabled = False
        self.embed.model.add_participant(self.values[0])
        self.view.save_button.is_participant_added = True
        self.view.save_button.maybe_able()
        await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())


class RemoveParticipantSelect(ui.Select):
    def __init__(self, embed):
        super().__init__(placeholder="Select a participant to remove", min_values=1, max_values=1, options=[
            discord.SelectOption(label=p.name, value=p.id) for p in embed.model.participants])
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.remove_item(self)
        self.view.remove_participant_button.disabled = False
        self.embed.model.remove_participant(self.values[0])
        await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())


class AddDescriptionModal(ui.Modal):
    def __init__(self, view: ScheduleEventView, embed: discord.Embed):
        super().__init__(title="Add Info", timeout=120.0)
        default_name = embed.model.name if embed.model.name else "Dungeons and Dragons"
        default_duration = embed.model.duration if embed.model.duration else "120"
        default_description = embed.model.description
        default_start_date = utils.date_to_str(
            embed.model.start_date if embed.model.start_date else datetime.now())
        default_end_date = utils.date_to_str(
            embed.model.end_date if embed.model.end_date else datetime.now() + timedelta(days=7))
        self.view = view
        self.embed = embed
        self.name = ui.TextInput(label="Name",
                                 default=default_name, required=True)
        self.add_item(self.name)
        self.description = ui.TextInput(label="Description",
                                        default=default_description, required=False)
        self.add_item(self.description)
        self.duration = ui.TextInput(label="Duration(min)",
                                     default=default_duration, required=True)
        self.add_item(self.duration)
        self.start_time = ui.TextInput(
            label="FROM", placeholder="DD/MM/YYYY", default=default_start_date, required=True)
        self.add_item(self.start_time)
        self.end_time = ui.TextInput(
            label="TO", placeholder="DD/MM/YYYY", default=default_end_date, required=True)
        self.add_item(self.end_time)

    def validate(self) -> str or None:
        """Returns the name of the field that is invalid or None if all fields are valid"""
        if not self.duration.value.isdigit():
            return "Duration"
        datetime_pattern = re.compile("\d{2}\/\d{2}\/\d{4}")
        if not re.fullmatch(datetime_pattern, self.start_time.value):
            return "Start Time"
        if not re.fullmatch(datetime_pattern, self.end_time.value):
            return "End Time"
        return None

    async def on_submit(self, interaction: Interaction) -> None:
        if field := self.validate():
            await interaction.response.send_message(utils.error_message(f"Invalid input: {field}"), ephemeral=True, )
            return

        self.view.add_description_button.label = "Edit Info"
        self.view.add_description_button.style = discord.ButtonStyle.secondary
        self.embed.model.name = self.name.value
        self.embed.model.description = self.description.value
        self.embed.model.duration = self.duration.value
        self.embed.model.set_start_date(self.start_time.value)
        self.embed.model.set_end_date(self.end_time.value)

        self.view.save_button.is_info_added = True
        self.view.save_button.maybe_able()

        await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(utils.error_message(str(error)), ephemeral=True)
