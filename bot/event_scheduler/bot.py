"""Python Bot Handling commands and events"""
import os
import discord
import logging
import event_scheduler.ui.schedule_event_message as schedule_event
from discord import app_commands
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


@bot.tree.command(name='schedule-event')
async def add_event(interaction: discord.Interaction) -> None:
    """Adds an event to the database"""
    embed = schedule_event.ScheduleEventEmbed()
    view = schedule_event.ScheduleEventView(embed=embed)
    await interaction.response.send_message('Schedule Event', view=view, embed=embed)
