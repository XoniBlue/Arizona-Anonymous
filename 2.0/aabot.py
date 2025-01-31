import nextcord
from nextcord.ext import commands
import os
import sys
from dotenv import load_dotenv
import json
import logging
import threading
import subprocess
from colorlog import ColoredFormatter

# Load Environment Variable from the .env file
load_dotenv()

# Set up colorized logging
formatter = ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',  # Color formatting
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'magenta',
    }
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# Custom loggers for different message types
json_logger = logging.getLogger("json")
json_logger.addHandler(console_handler)
json_logger.setLevel(logging.INFO)

cog_logger = logging.getLogger("cogs")
cog_logger.addHandler(console_handler)
cog_logger.setLevel(logging.INFO)

# Create an instance of the bot
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True  # Enable the members intent
bot = commands.Bot(command_prefix="$", intents=intents, chunk_guilds_at_startup=False)

json_data = {}

# Load JSON files from a directory
def load_json_files(directory_path):
    """Loads JSON files from a given directory and logs only the filenames."""
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data[filename[:-5]] = json.load(f)
                print(f"[✅] Loaded {filename} Successfully!")
            except json.JSONDecodeError as e:
                print(f"[❌] Failed to Load {filename}: {e}")

# Example usage: load JSON files from "./json" directory
load_json_files("./json")

# Function to dynamically load cogs
def load_cogs(bot):
    """Load all cogs from the 'cogs' directory and log status."""
    cog_dir = "cogs"
    
    if not os.path.exists(cog_dir):
        print(f"[⚠️] Cog directory '{cog_dir}' not found!")
        return
    
    for filename in os.listdir(cog_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"cogs.{filename[:-3]}"  # Remove ".py" extension
            try:
                bot.load_extension(cog_name)  # Load the cog without awaiting here
                print(f"[✅] Loaded cog: {cog_name}")
            except Exception as e:
                print(f"[❌] Failed to load cog {cog_name}: {type(e).__name__} - {e}")

# Function to run FastAPI in a separate thread
def run_fastapi():
    subprocess.run([sys.executable, "-m", "uvicorn", "cogs.fastapi_cog:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])


# Function to run Flask
def run_flask():
    subprocess.run(["python", "cogs/flask_cog.py"])

# Event when the bot is ready
@bot.event
async def on_ready():
    activity = nextcord.CustomActivity(name="Recovery Support !help")  # Game type with no prefix like 'Playing'
    # Force the bot to cache all members
    await bot.guilds[0].chunk()  # Assumes the bot is in only one server
    await bot.change_presence(status=nextcord.Status.online, activity=activity)
    logger.info(f"Bot is ready and logged in as {bot.user}")
    
    # Load all cogs dynamically
    load_cogs(bot)

    # After loading the cogs, start the task from the meditation (meditation) cog
    meditation_cog = bot.get_cog("MeditationCog")  # Ensure the correct cog name (likely "MeditationCog")
    if meditation_cog:
        logger.info("Meditation cog loaded successfully.")
    else:
        logger.warning("The meditation cog is not loaded properly.")
        
        # Start FastAPI and Flask in separate threads
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()
    
    run_flask()

# Start the bot with your token
bot.run(os.getenv('DISCORD_TOKEN'))
