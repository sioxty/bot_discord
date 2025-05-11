import disnake
from disnake.ext import commands
import logging
import os
from config import TOKEN

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all())

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

directory = 'cogs'

for filename in os.listdir(directory):
    if filename.endswith(".py"):
        if filename != "__init__.py":
            log.info(filename)
            bot.load_extension(f"{directory}.{filename[:-3]}")


@bot.event
async def on_ready():
    log.info("Bot is ready!")

bot.run(token=TOKEN)