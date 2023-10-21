import discord
import re
from discord import ui
from discord.interactions import Interaction
from event_scheduler.api.data_models import EventModel


class ScheduleEventEmbed(discord.Embed):
    def __init__(self, model: EventModel = None):
        super().__init__(title="Schedule Event", color=discord.Color.pink())
        self.model = model if model else EventModel()

    def reload_embed(self):
        self.clear_fields()
        self.add_field(name="Event Name",
                       value=self.model.name, inline=False)
        if self.model.description:
            self.add_field(name="Description",
                           value=self.model.description, inline=False)
        self.add_field(
            name="Participants", value=self.model.get_trunc_participants(), inline=False)
        if self.model.tags:
            self.add_field(
                name="Tags", value=self.model.get_trunc_tags(), inline=False)
        return self


class ScheduleEventView(ui.View):
    """View for scheduling an event"""

    def __init__(self, embed: discord.Embed = None):
        super().__init__()
        self.embed = embed if embed else ScheduleEventEmbed()
        self.embed = self.embed.reload_embed()
        self.add_participant_button = AddParticipantButton(self.embed)
        self.add_item(self.add_participant_button)
        self.add_description_button = AddDescriptionButton(self.embed)
        self.add_item(self.add_description_button)
        self.save_button = SaveButton(self.embed)
        self.add_item(self.save_button)


# Buttons


class AddParticipantButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Add Participant", style=discord.ButtonStyle.primary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.add_item(SelectParticipant(self.embed))
        self.style = discord.ButtonStyle.secondary
        self.disabled = True
        await interaction.message.edit(view=self.view)


class AddDescriptionButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Add Info", style=discord.ButtonStyle.primary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(AddDescriptionModal(self.view, self.embed))


class SaveButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Save", style=discord.ButtonStyle.green)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        if self.embed.model.save_in_database():
            await interaction.message.edit(content="Event created!", embed=None, view=None)
        else:
            await interaction.response.send_message("Ups, something went wrong!")


# UI Objects


class SelectParticipant(ui.MentionableSelect):
    def __init__(self, embed):
        super().__init__(placeholder="Select a participant", min_values=1, max_values=1)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.remove_item(self)
        self.view.add_participant_button.disabled = False
        self.embed.model.add_participant(self.values[0])
        await interaction.message.edit(view=self.view, embed=self.embed.reload_embed())


class AddDescriptionModal(ui.Modal):
    name = ui.TextInput(label="Event name",
                        default="Dungeons and Dragons", required=True)
    description = ui.TextInput(
        label="Description", placeholder="Meeting", style=discord.TextStyle.long, required=False)
    tags = ui.TextInput(label="Tags", placeholder="DnD,Meeting",
                        style=discord.TextStyle.short, required=False)
    start_time = ui.TextInput(
        label="From", placeholder="DD/MM/YYYY", required=True)
    end_time = ui.TextInput(
        label="To", placeholder="DD/MM/YYYY", required=True)

    def __init__(self, view: ScheduleEventView, embed: discord.Embed):
        super().__init__(title="Add Info", timeout=120.0)
        self.view = view
        self.embed = embed
        if self.embed.model.name:
            self.name.value = self.embed.model.name
        if self.embed.model.description:
            self.description.value = self.embed.model.description

    def validate(self) -> str or None:
        """Returns the name of the field that is invalid or None if all fields are valid"""
        return None  # TODO: fix this
        tags_pattern = re.compile("[a-zA-Z0-9]+(,[a-zA-Z0-9]+)*")
        datetime_pattern = re.compile("\d{2}\.\d{2}\.\d{2}")
        if self.tags and not re.fullmatch(tags_pattern, self.tags.value):
            return "Tags"
        if not re.fullmatch(datetime_pattern, self.start_time.value):
            return "Start Time"
        if not re.fullmatch(datetime_pattern, self.end_time.value):
            return "End Time"
        return None

    async def on_submit(self, interaction: Interaction) -> None:
        if field := self.validate():
            # This weird thing below is to make the text red
            await interaction.response.send_message(f"```ansi\n\u001b[31mInvalid input: {field}\n```", ephemeral=True, )
            return

        self.view.add_description_button.label = "Edit Info"
        self.view.add_description_button.style = discord.ButtonStyle.secondary
        self.embed.model.name = self.name.value
        self.embed.model.description = self.description.value
        self.embed.model.add_tags(self.tags.value)
        self.embed.model.start_date = self.start_time.value
        self.embed.model.end_date = self.end_time.value

        await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)
