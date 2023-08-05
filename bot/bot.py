"""Python Bot which schedules events for the server"""
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    """Sets up slash commands and prints if ready"""
    print('Bot is ready!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Exception while syncing slash commands: {e}")

@bot.tree.command(name="hello_there")
async def hello_there(interaction: discord.Interaction):
    """Says hello there"""
    await interaction.response.send_message("General Kenobi!", ephemeral=True)

bot.run(os.getenv('TOKEN'))
