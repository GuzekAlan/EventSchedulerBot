"""Python Bot Handling commands and events"""
import os
import logging
import discord
import event_scheduler.utils as utils
from event_scheduler.api.event_model import EventModel
from event_scheduler.api.availability_model import AvailabilityModel
from event_scheduler.api.settings import upsert_bot_channel_id, get_bot_channel_id
from event_scheduler.ui.show_events_message import ShowEventsEmbed
from event_scheduler.ui.schedule_event_message import ScheduleEventEmbed, ScheduleEventView
from event_scheduler.ui.select_dates_message import SelectDatesView
from event_scheduler.ui.reschedule_event_message import RescheduleEventView
from event_scheduler.ui.cancel_event_message import CancelEventView
from event_scheduler.db import get_database
from discord.ext import commands
from discord import app_commands
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
async def on_start_schedule_event(event_id: int, member_id) -> None:
    """Starts the schedule event"""
    if user := bot.get_user(member_id):
        await user.send(utils.information_message(f"Select dates for event: {event_id}"))


@bot.event
async def on_save_availability(model: AvailabilityModel) -> None:
    """Checks if every user submitted and optional picks date with most votes"""
    if event_model := EventModel.get_from_database(model.event_id, bot, "created"):
        if event_model.not_answered() == 0:
            if bot_channel := bot.get_channel(get_bot_channel_id(
                    event_model.guild_id)):
                if error := event_model.choose_date():
                    await bot_channel.send(utils.error_message(error))
                else:
                    await bot_channel.send("**Event's date confirmed**", view=None, embed=ScheduleEventEmbed(
                        event_model, "Scheduled Event").reload_embed())
            else:
                await bot.get_user(event_model.creator_id).send(utils.error_message(
                    f'Bot channel in guild {bot.get_guild(event_model.guild_id).name} not set'))


@bot.tree.command(name='schedule-event')
async def add_event(interaction: discord.Interaction) -> None:
    """Adds an event to the database"""
    model = EventModel(creator_id=interaction.user.id,
                       guild_id=interaction.guild.id)
    view = ScheduleEventView(bot=bot, model=model)
    await interaction.response.send_message(view=view, embed=view.embed)


@bot.tree.command(name='show-events')
@app_commands.choices(status=[app_commands.Choice(name=s.capitalize(), value=s) for s in ["created", "confirmed", "canceled"]])
async def show_events(interaction: discord.Interaction, status: app_commands.Choice[str]) -> None:
    """Shows events with specified status"""
    if events := EventModel.get_from_database_by_creator(
        creator_id=interaction.user.id,
        bot=bot,
        status=status.value
    ):
        return await interaction.response.send_message(embed=ShowEventsEmbed(events, status.value))
    await interaction.response.send_message(utils.information_message("No events found"))


@bot.tree.command(name='reschedule-event')
@app_commands.choices(status=[app_commands.Choice(name=s.capitalize(), value=s) for s in ["created", "confirmed", "canceled"]])
async def reschedule_event(interaction: discord.Interaction, status: app_commands.Choice[str]):
    view = RescheduleEventView(interaction.user.id, status.value, bot=bot)
    await interaction.response.send_message(view=view)


@bot.tree.command(name='cancel-event')
async def cancel_event(interaction: discord.Interaction):
    view = CancelEventView(interaction.user.id, bot=bot)
    await interaction.response.send_message(view=view)


@bot.tree.command(name='select-dates')
@app_commands.describe(event_id="Event ID")
async def select_dates(interaction: discord.Interaction, event_id: str):
    await interaction.response.send_message(utils.information_message("Looking for event..."), ephemeral=True)
    if event_model := EventModel.get_from_database(event_id, bot, "created"):
        model = AvailabilityModel(event_id, interaction.user.id, event_model.start_date,
                                  event_model.end_date)
        view = SelectDatesView(
            bot=bot, event_name=event_model.get_name(), availability_model=model, user_ids=event_model.get_participants_ids())
        await interaction.user.send(view=view, embed=view.embed)
    else:
        await interaction.user.send(utils.error_message("Event not found"))


@bot.command(name="set-channel")
async def set_channel(ctx: commands.Context):
    """Sets channel for bot to send messages"""
    if ctx.message.author.guild_permissions.administrator:
        if upsert_bot_channel_id(ctx.guild.id, ctx.channel.id):
            return await ctx.send(utils.information_message("Channel set"))
        return await ctx.send(utils.error_message("Error while setting channel"))
    return await ctx.message.reply(utils.error_message("You don't have permission to do that"))
