import os
import asyncio
import discord
import flask
from discord import Interaction
from discord.app_commands import commands
from flask import Flask
from threading import Thread
import phonenumbers
from phonenumbers import timezone, geocoder, carrier
import dotenv
from virustotal_python import Virustotal
from base64 import  urlsafe_b64encode
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import webserver
from io import BytesIO
import qrcode

load_dotenv()

DISCORD_TOKEN = os.environ['DISCORD_BOT_TOKEN']
VIRUSTOTAL_KEY = os.environ['VIRUSTOTAL_API_TOKEN']


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is ready to dive in!")

@bot.tree.command(name="poll", description="Send a poll.")
async def poll(interaction: discord.Interaction, question: str):
    await interaction.response.defer(ephemeral=True)
    msg = await interaction.channel.send(f"**{interaction.user.name()}** asks: {question}")
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.tree.command(name="assign", description="Assign me a role")
@app_commands.describe(role="The role to assign")
async def assign(interaction: discord.Interaction, role: str):
    guild = interaction.guild
    member = interaction.user

    #find role by name
    role_obj = discord.utils.get(guild.roles, name=role)
    if not role_obj:
        return await interaction.response.send_message(f"Role `{role}` does not exist!", ephemeral=True)

    if role_obj in member.roles:
        return await interaction.response.send_message(f'You already have "**__{role}__**" king')

    if role_obj >= guild.me.top_role:
        return await interaction.response.send_message(f"I cant assign you as {role}", ephemeral=True)

    await member.add_roles(role_obj)
    await interaction.response.send_message(f"Assignment done!", ephemeral=True)

@bot.tree.command(name="clear", description="Clear messages")
@app_commands.describe(message="How many message to clear")
async def clear(interaction: discord.Interaction, message: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(f"You don't have permission to do that!", ephemeral=True)
    if message < 1 or message > 100:
        return await interaction.response.send_message(f"Message must be between 1 and 100", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=message)
    await interaction.followup.send(f'Cleared **{len(deleted)}** messages!', ephemeral=True)

@bot.tree.command(name="number", description="Find numbers location carrier timezone")
@app_commands.describe(number="The number to find Enter number without plus")
async def number(interaction: discord.Interaction, number: int):
    await interaction.response.defer(ephemeral=True)
    numb = "+" + str(number)

    parsed = phonenumbers.parse(numb)
    _location = geocoder.description_for_number(parsed, "en")
    _carrier = carrier.name_for_number(parsed, "en")
    _timezone = timezone.time_zones_for_number(parsed)

    try:
        await interaction.followup.send(f'The location of that number is **__{_location}__**')
        await interaction.followup.send(f'The timezone of that number is **__{_timezone}__**')
        await interaction.followup.send(f'The carrier of that number is **__{_carrier}__**')
    except Exception as e:
        await interaction.followup.send(f'An error occurred: __{e}__', ephemeral=True)




@bot.tree.command(name="phishcheck", description="Check if the URL is safe or not")
@app_commands.describe(url="The URL to check")
async def phishcheck(interaction: discord.Interaction, url: str):
    await interaction.response.defer(ephemeral=True)

    with Virustotal(VIRUSTOTAL_KEY) as vtotal:
        try:
            resp = vtotal.request("urls", data={"url": url}, method="POST")
            await asyncio.sleep(10)
            url_id = urlsafe_b64encode(url.encode()).decode().strip("=")

            report = vtotal.request(f"urls/{url_id}")

            stats = report.data["attributes"]["last_analysis_stats"]
            mal = stats.get("malicious", 0)
            sus = stats.get("suspicious", 0)
            if mal > 0:
                verdict = f'MALICIOUS Detected by **__{mal}__** engines'
            elif sus > 0:
                verdict = f'SUS Detected by **__{sus}__** engines'
            else:
                verdict = f"The URL is clean"

            await interaction.followup.send(verdict, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error **{e}**", ephemeral=True)


@bot.tree.command(name="qrcode", description="Generate QR code")
@app_commands.describe(url="The URL to check", fg="Foreground color", bg="Background color")
async def generate_qrcode(interaction: discord.Interaction, url: str, fg: str = "white", bg: str = "black"):
    await interaction.response.defer(ephemeral=True)

    try:

        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fg, back_color=bg)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        file = discord.File(fp=buffer, filename="qrcode.png")
        await interaction.followup.send(file=file)
    except Exception as e:
        await interaction.followup.send(f"Error **{e}**", ephemeral=True)



webserver.keep_alive()
bot.run(DISCORD_TOKEN)
