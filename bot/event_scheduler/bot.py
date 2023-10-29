"""Python Bot Handling commands and events"""
import os
import logging
import discord
from event_scheduler.api.data_models import EventModel
from event_scheduler.db import get_database
from event_scheduler.ui.schedule_event_message import ScheduleEventView
from event_scheduler.ui.select_dates_message import SelectDatesView
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

# Setting up bot

bot = commands.Bot(command_prefix='!',
                   description="Set of commands to pick perfect date for your event", intents=discord.Intents.all())
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a')


def run_bot() -> None:
    """Runs the bot"""
    bot.run(os.getenv('TOKEN'), log_handler=handler, log_level=logging.INFO)

# Bot interactions


@bot.event
async def on_ready() -> None:
    """Sets up slash commands and prints if ready"""
    print('Bot is ready!')
    try:
        synced = await bot.tree.sync()
        print(f"Bot synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Exception while syncing slash commands: {e}")


@bot.event
async def on_start_schedule_event(event_id: int, member_id, event_model: EventModel) -> None:
    """Starts the schedule event"""
    user = bot.get_user(member_id)
    view = SelectDatesView(bot=bot, event_model=event_model)
    print(f"Sending message to {user.name}")
    await user.send('Pick Dates for your event!', view=view, embed=view.embed)


@bot.tree.command(name='schedule-event')
async def add_event(interaction: discord.Interaction) -> None:
    """Adds an event to the database"""
    view = ScheduleEventView(bot=bot)
    await interaction.response.send_message('Schedule Event', view=view, embed=view.embed)
