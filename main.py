import discord
from discord.ext import commands

import yaml
from utils import TicketPanel

# Bot configuration
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# Load config
def load_config():
    with open("config.yml", "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

config = load_config()

# Bot metadata
bot.version = "v1.0"

@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")
    
    # Load cogs
    await bot.load_extension("cogs.auto-thread")
    await bot.load_extension("cogs.keywords")
    await bot.load_extension("cogs.mod")

    await bot.tree.sync()
    
    print("All cogs loaded!")

# Run the bot
bot.run(config["token"])
