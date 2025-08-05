import disnake
from disnake.ext import commands
import logging
import os
from aiosoundcloud import get_client_id

from cogs.core.exception import BaseBotException
from config import TOKEN, CLIENT_ID

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all())

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

directory = "cogs"
for filename in os.listdir(directory):
    if filename.endswith(".py"):
        if filename != "__init__.py":
            log.info(filename)
            bot.load_extension(f"{directory}.{filename[:-3]}")


@bot.event
async def on_ready():
    CLIENT_ID = await get_client_id()
    log.info(f"Bot is ready {bot.user.name}#{bot.user.discriminator}")


@bot.event
async def on_slash_command_error(inter, error):
    orig = getattr(error, "original", error)
    if isinstance(orig, BaseBotException):
        try:
            if not inter.response.is_done():
                await inter.response.defer()
            await inter.send(str(orig), ephemeral=True)
        except disnake.errors.InteractionTimedOut:
            log.warning("Interaction timed out, cannot send error message.")
    else:
        raise error


bot.run(token=TOKEN)
