"""Python Bot Handling commands and events"""
import os
import discord
import logging
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
from event_scheduler.db import get_database
from event_scheduler import api
from event_scheduler.utils import *
from event_scheduler.ui.view import ScheduleEventView, ScheduleEventEmbed

bot = commands.Bot(command_prefix='!', description="Set of commands to pick perfect date for your event", intents=discord.Intents.all())
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a')

@bot.event
async def on_ready() -> None:
    """Sets up slash commands and prints if ready"""
    print('Bot is ready!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Exception while syncing slash commands: {e}")

@bot.tree.command(name='add_user')
@app_commands.describe(user='Which User to Add')
async def add_user(interaction: discord.Interaction, user: str) -> None:
    """Adds a user to the database"""
    if api.add_user(get_database(), user):
        await interaction.response.send_message(f"Added user: {user}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Failed to add {user}", ephemeral=True)

@bot.tree.command(name='list_users')
async def list_users(interaction: discord.Interaction) -> None:
    """Lists all users in the database"""
    users = api.list_users(get_database())
    if users:
        await interaction.response.send_message(f"Users: {users_list(users)}", ephemeral=True)
    else:
        await interaction.response.send_message(f"No users found", ephemeral=True)

@bot.tree.command(name='schedule_event')
async def add_event(interaction: discord.Interaction) -> None:
    """Adds an event to the database"""
    embed = ScheduleEventEmbed()
    view = ScheduleEventView(embed=embed)
    await interaction.response.send_message('Schedule Event', view=view, embed=embed)


def run_bot() -> None:
    """Runs the bot"""
    bot.run(os.getenv('TOKEN'), log_handler=handler, log_level=logging.INFO)
