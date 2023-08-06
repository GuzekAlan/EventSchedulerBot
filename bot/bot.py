"""Python Bot Handling commands and events"""
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
from bot.db import get_database
from bot import api
from bot.utils import *

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

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
        await interaction.response.send_message(f"Added {user} to the database", ephemeral=True)
    else:
        await interaction.response.send_message(f"Failed to add {user} to the database", ephemeral=True)

@bot.tree.command(name='list_users')
async def list_users(interaction: discord.Interaction) -> None:
    """Lists all users in the database"""
    users = api.list_users(get_database())
    if users:
        await interaction.response.send_message(f"Users: {users_list(users)}", ephemeral=True)
    else:
        await interaction.response.send_message(f"No users found", ephemeral=True)

def run_bot() -> None:
    """Runs the bot"""
    bot.run(os.getenv('TOKEN'))
