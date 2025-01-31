import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import logging
import colorlog
from threading import Thread
from flask import Flask, render_template, request, redirect, url_for

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Set up colorized logging
log_format = "%(log_color)s[%(levelname)s] %(message)s"
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

# Create bot instance
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)

formatter = colorlog.ColoredFormatter(log_format, log_colors=log_colors)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Load cogs dynamically
def load_cogs():
    for cog in ['config', 'daily', 'meditation', 'sponsor']:
        bot.load_extension(f'cogs.{cog}')

# Flask route to manage cogs
@app.route('/')
def index():
    # List all cogs and their status
    cogs = [filename[:-3] for filename in os.listdir("./cogs") if filename.endswith(".py")]
    return render_template("index.html", cogs=cogs)

@app.route('/toggle_cog', methods=["POST"])
def toggle_cog():
    cog_name = request.form["cog_name"]
    action = request.form["action"]

    try:
        # Run the loading/unloading operation in the bot's event loop
        if action == "disable":
            bot.loop.create_task(unload_cog(cog_name))
        elif action == "enable":
            bot.loop.create_task(load_cog(cog_name))
        return redirect(url_for("index", message=f"{cog_name} has been {action}d"))
    except Exception as e:
        return f"Error: {e}"

# Function to unload a cog in the bot's event loop
async def unload_cog(cog_name):
    try:
        bot.unload_extension(f"cogs.{cog_name}")
        logger.info(f"✅ Cog '{cog_name}' unloaded successfully")
    except Exception as e:
        logger.error(f"❌ Error unloading cog '{cog_name}': {e}")

# Function to load a cog in the bot's event loop
async def load_cog(cog_name):
    try:
        bot.load_extension(f"cogs.{cog_name}")
        logger.info(f"✅ Cog '{cog_name}' loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading cog '{cog_name}': {e}")

# Start Flask app in a separate thread so it doesn't block the bot
def start_flask():
    app.run(debug=True, use_reloader=False, port=5001)

# Log when the bot is ready
@bot.event
async def on_ready():
    logger.info(f"✅ Bot is logged in as {bot.user}")
    
    # Load cogs dynamically
    load_cogs()
    
    activity = nextcord.Game(name="Recovery Support !help")
    
    # Cache all members
    await bot.guilds[0].chunk()  # Assumes the bot is in only one server
    await bot.change_presence(status=nextcord.Status.online, activity=activity)
    
    logger.info("✅ Cogs loaded successfully")
    
    # Start Flask in a separate thread
    thread = Thread(target=start_flask)
    thread.start()

# Log when a command is invoked
@bot.event
async def on_command(ctx):
    logger.info(f"📥 Command received: {ctx.command} from {ctx.author} (ID: {ctx.author.id}) in #{ctx.channel}")

# Log after a command completes execution
@bot.event
async def on_command_completion(ctx):
    logger.info(f"📤 Command executed: {ctx.command} sent back to {ctx.author}")

# Log command errors
@bot.event
async def on_command_error(ctx, error):
    logger.error(f"❌ Error in command {ctx.command}: {error}")

# Example command for testing
@bot.command()
async def hello(ctx):
    response = f"Hello, {ctx.author.name}!"
    await ctx.send(response)
    logger.info(f"📤 Response sent: {response}")

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
