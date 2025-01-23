import discord
import tempfile
from downloader import *

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# ---------------------------


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("$download "):
        parts = message.content.split(" ")
        url = parts[1]
        title = None
        artist = None
        if len(parts) > 2:
            for opt in parts[2:]:
                key, value = opt.split("=")
                if key == "title":
                    title = value
                if key == "artist":
                    artist = value

        await message.channel.send(
            f"downloading {url}, please be patient... \ntitle = {title or '(default)'}\nartist = {artist or '(default)'}"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            downloaded_file = download(
                url,
                downloads_folder=temp_dir,
                overrides_file="channel_overrides.json",
                title=title,
                artist=artist,
            )
            await message.channel.send(file=discord.File(downloaded_file))


# ----------------------------

client.run(os.getenv("TOKEN"))
