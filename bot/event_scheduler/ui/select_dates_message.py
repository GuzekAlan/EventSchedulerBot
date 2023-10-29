import discord
import event_scheduler.utils as utils
from discord import ui
from discord.interactions import Interaction
from event_scheduler.api.data_models import AvailibilityModel, EventModel
from datetime import time


class SelectDatesMessage(discord.Embed):
    def __init__(self, event_id: int, user_id: int, event_model: EventModel, availibility_model: AvailibilityModel = None):
        super().__init__(title=event_model.name, color=discord.Color.pink())
        self.model = availibility_model if availibility_model else AvailibilityModel(
            event_id,
            user_id,
            event_model.start_date,
            event_model.end_date
        )

    def reload_embed(self):
        formatted_date = utils.date_to_str(self.model.current_date)
        weekday = utils.weekday_name(self.model.current_date)
        self.clear_fields()
        self.add_field(name=formatted_date,
                       value=weekday, inline=False)
        return self


class SelectDatesView(ui.View):
    """View for selecting availibility for an event"""

    def __init__(self, event_id: int, user_id: int, event_model: EventModel, embed: discord.Embed = None, bot: discord.Client = None):
        super().__init__()
        self.bot = bot
        self.embed = embed if embed else SelectDatesMessage(
            event_id=event_id, user_id=user_id, event_model=event_model)
        self.embed = self.embed.reload_embed()
        self.add_item(ChangeDayButton(self.embed, "<<", "previous", 7))
        self.add_item(ChangeDayButton(self.embed, "<", "previous"))
        self.add_item(ChangeDayButton(self.embed, ">", "next"))
        self.add_item(ChangeDayButton(self.embed, ">>", "next", 7))
        self.add_item(SelectHours(self.embed, "ok"))
        self.add_item(SelectHours(self.embed, "maybe"))
        self.add_item(SelectHours(self.embed, "no"))
        self.add_item(SaveButton(self.embed))


# Buttons

class ChangeDayButton(ui.Button):
    def __init__(self, embed: discord.Embed, title: str, direction: str, days: int = 1):
        super().__init__(label=title, style=discord.ButtonStyle.primary)
        self.embed = embed
        self.direction = direction
        self.days = days

    async def callback(self, interaction: Interaction):
        if self.embed.model.change_day(self.direction, self.days):
            await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())
        else:
            await interaction.send_message("Error changing day")


class SaveButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Save", style=discord.ButtonStyle.green)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        if self.embed.model.save_in_database():
            self.view.bot.dispatch("save_availibility", self.embed.model)
            await interaction.response.edit_message(content="`Availibility saved :)`", embed=None, view=None)
        else:
            await interaction.response.send_message("Ups, something went wrong!")


# UI Objects


class SelectHours(ui.Select):
    def __init__(self, embed: discord.Embed, availibility: str):
        # TODO: Think how to add every 15 min (because maximal max_values is 25)
        super().__init__(placeholder=f"Select {availibility.upper()} Hours", min_values=1, max_values=24, options=list([
            discord.SelectOption(label=f"{time.hour}:00", value=f"{time.hour}") for time in AvailibilityModel.times
        ]))
        self.availibility = availibility
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.embed.model.add_times([time(hour=int(v))
                                   for v in self.values], self.availibility)
        await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())
