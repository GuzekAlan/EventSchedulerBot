from typing import Optional
import discord
from discord import ui
from discord.interactions import Interaction


class ScheduleEventEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="Schedule Event",
                         description="Schedule an event", color=discord.Color.pink())


class ScheduleEventView(ui.View):
    """View for scheduling an event"""

    def __init__(self, embed: discord.Embed = None):
        super().__init__()
        self.embed = embed
        self.add_participant_button = AddParticipantButton(self.embed)
        self.add_item(self.add_participant_button)
        self.add_description_button = AddDescriptionButton(self.embed)
        self.add_item(self.add_description_button)


# Buttons


class AddParticipantButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Add Participant", style=discord.ButtonStyle.secondary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.disabled = True
        self.view.add_item(SelectParticipant(self.embed))
        await interaction.message.edit(view=self.view)


class AddDescriptionButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Add Description", style=discord.ButtonStyle.secondary)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(AddDescriptionModal(self.view, self.embed))


# UI Objects


class SelectParticipant(ui.MentionableSelect):
    def __init__(self, embed):
        super().__init__(placeholder="Select a participant", min_values=1, max_values=1)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.view.remove_item(self)
        self.view.add_participant_button.disabled = False
        self.embed.add_field(name="Participants", value=", ".join(
            [participant.mention for participant in self.values]))
        await interaction.message.edit(view=self.view, embed=self.embed)


class AddDescriptionModal(ui.Modal):
    name = ui.TextInput(label="Event name", default="Dungeons and Dragons")

    def __init__(self, view: ScheduleEventView, embed: discord.Embed):
        super().__init__(title="Add Description", timeout=120.0)
        self.view = view
        self.embed = embed

    async def on_submit(self, interaction: Interaction) -> None:
        self.embed.insert_field_at(
            0, name="Event Name", value=self.name.value, inline=False)
        self.view.add_description_button.disabled = True
        await interaction.response.edit_message(view=self.view, embed=self.embed)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)
