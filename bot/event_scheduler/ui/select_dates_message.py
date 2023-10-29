import discord
from discord import ui
from discord.interactions import Interaction
from event_scheduler.api.data_models import AvalibilityModel, EventModel


class SelectDatesMessage(discord.Embed):
    def __init__(self, event_model: EventModel, availibility_model: AvalibilityModel = None):
        super().__init__(title=event_model.name, color=discord.Color.pink())
        self.model = availibility_model if availibility_model else AvalibilityModel(
            event_model.start_date)

    def reload_embed(self):
        self.clear_fields()
        self.add_field(name=self.model.current_date,
                       value=self.model.current_date, inline=False)
        return self


class SelectDatesView(ui.View):
    """View for selecting availibility for an event"""

    def __init__(self, event_model: EventModel, embed: discord.Embed = None, bot: discord.Client = None):
        super().__init__()
        self.bot = bot
        self.embed = embed if embed else SelectDatesMessage(
            event_model=event_model)
        self.embed = self.embed.reload_embed()
        self.previous_day_button = ChangeDayButton(
            self.embed,  "Previous Day", "previous")
        self.add_item(self.previous_day_button)
        self.next_day_button = ChangeDayButton(self.embed, "Next Day", "next")
        self.add_item(self.next_day_button)


# Buttons

class ChangeDayButton(ui.Button):
    def __init__(self, embed: discord.Embed, title: str, direction: str):
        super().__init__(label=title, style=discord.ButtonStyle.primary)
        self.embed = embed
        self.direction = direction

    async def callback(self, interaction: Interaction):
        if self.embed.model.change_day(self.direction):
            await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())
        else:
            await interaction.send("Error changing day")
