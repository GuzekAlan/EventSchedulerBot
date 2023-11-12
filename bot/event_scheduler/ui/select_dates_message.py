import discord
import event_scheduler.utils as utils
from discord import ui
from discord.interactions import Interaction
from event_scheduler.api.availibility_model import AvailibilityModel
from event_scheduler.api.event_model import EventModel
from datetime import time


class SelectDatesMessage(discord.Embed):
    def __init__(self, event_name: str, availibility_model: AvailibilityModel):
        super().__init__(title=event_name, color=discord.Color.pink())
        self.model = availibility_model

    def reload_embed(self):
        formatted_date = utils.date_to_str(self.model.current_date)
        weekday = utils.weekday_name(self.model.current_date)
        self.clear_fields()
        self.add_field(name=formatted_date,
                       value=weekday, inline=False)
        return self


class SelectDatesView(ui.View):
    """View for selecting availibility for an event"""

    def __init__(self, event_name: str, availibility_model: AvailibilityModel, bot: discord.Client):
        super().__init__()
        self.bot = bot
        self.embed = SelectDatesMessage(
            event_name=event_name, availibility_model=availibility_model)
        self.embed = self.embed.reload_embed()
        self.add_item(ChangeDayButton(self.embed, "<<", "previous", 7))
        self.add_item(ChangeDayButton(self.embed, "<", "previous"))
        self.add_item(ChangeDayButton(self.embed, ">", "next"))
        self.add_item(ChangeDayButton(self.embed, ">>", "next", 7))
        self.select_ok_hours = SelectHours(self.embed, "ok")
        self.add_item(self.select_ok_hours)
        self.select_maybe_hours = SelectHours(self.embed, "maybe")
        self.add_item(self.select_maybe_hours)
        self.add_item(SaveButton(self.embed))

    def refresh_selectes(self):
        self.remove_item(self.select_ok_hours)
        self.remove_item(self.select_maybe_hours)
        self.select_ok_hours = SelectHours(self.embed, "ok")
        self.add_item(self.select_ok_hours)
        self.select_maybe_hours = SelectHours(self.embed, "maybe")
        self.add_item(self.select_maybe_hours)


# Buttons

class ChangeDayButton(ui.Button):
    def __init__(self, embed: discord.Embed, title: str, direction: str, days: int = 1):
        super().__init__(label=title, style=discord.ButtonStyle.primary)
        self.embed = embed
        self.direction = direction
        self.days = days

    async def callback(self, interaction: Interaction):
        if self.embed.model.change_day(self.direction, self.days):
            self.view.refresh_selectes()
            await interaction.response.edit_message(view=self.view, embed=self.embed.reload_embed())
        else:
            await interaction.send_message("Error changing day")


class SaveButton(ui.Button):
    def __init__(self, embed: discord.Embed):
        super().__init__(label="Save", style=discord.ButtonStyle.green)
        self.embed = embed

    async def callback(self, interaction: Interaction):
        # TODO: Add no hours based on ok and maybe hours
        if self.embed.model.save_in_database():
            self.view.bot.dispatch("save_availibility", self.embed.model)
            await interaction.response.edit_message(content="`Availibility saved :)`", embed=None, view=None)
        else:
            await interaction.response.send_message("Ups, something went wrong!")


# UI Objects


class SelectHours(ui.Select):
    def __init__(self, embed: discord.Embed, availibility: str):
        super().__init__(
            placeholder=f"Select {availibility.upper()} Hours",
            min_values=0,
            max_values=24,
            options=list([
                discord.SelectOption(
                    label=f"{time.hour}:00",
                    value=f"{time.hour}",
                    default=embed.model.is_time_checked(time, availibility)
                ) for time in AvailibilityModel.times
            ])
        )
        self.availibility = availibility
        self.embed = embed

    async def callback(self, interaction: Interaction):
        self.embed.model.add_times([time(hour=int(v))
                                   for v in self.values], self.availibility)
        await interaction.response.defer()
