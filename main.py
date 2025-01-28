import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import json
import random
import pytz
import logging
import requests
import csv
from io import StringIO
import threading
from lxml import html
from datetime import datetime
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Load Configuration
def load_config():
    with open("json/config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

# Load the user's time zone
def load_user_timezones():
    try:
        with open("json/user_timezones.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
# Save the user's time zone
def save_user_timezones(user_timezones):
    with open("json/user_timezones.json", "w", encoding="utf-8") as f:
        json.dump(user_timezones, f, indent=4)

# Load daily thoughts from the local JSON file
def fetch_daily_thoughts():
    try:
        with open("json/daily_thoughts.json", "r", encoding="utf-8") as f:
# Attempt to load the JSON data
            content = f.read()
            try:
# If the file contains multiple JSON objects, split them
# You could adjust this approach based on the format you're working with
                daily_thoughts = json.loads(f"[{content.replace('}{', '},{')}]")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None

# Prepare the dictionary to store thoughts
            daily_thoughts_data = {}

            for thought in daily_thoughts:
                date_str = thought.get("date")
                if date_str and "quote" in thought:
# Try to parse the date in "MMMM dd" format
                    try:
                        parsed_date = datetime.strptime(date_str, "%B %d").strftime("%B %d")
                    except ValueError:
                        print(f"Invalid date format: {date_str}")
                        continue

# Extract the thought details
                    daily_thoughts_data[parsed_date] = {
                        "quote": thought["quote"],
                        "reflection": thought.get("reflection", ""),
                        "prayer": thought.get("prayer", "")
                    }
            return daily_thoughts_data

    except FileNotFoundError:
        print("Daily thoughts file not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable the members intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Dismiss button functionality
class DismissButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.danger)
    async def dismiss(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Correct way to delete the message using the interaction object
        await interaction.message.delete()  # This will delete the message when the button is clicked
        await interaction.response.send_message("The message has been dismissed.", ephemeral=True)

# Command to send a message with the dismiss button
@bot.command()
async def send(ctx):
    view = DismissButton()
    await ctx.send("Click to dismiss!", view=view)
    logger.info(f"Sent dismiss message to {ctx.channel.name}")

# Get a random meditation quote
def get_random_meditation_quote():
    static_content = load_static_content()
    meditation_quotes = static_content.get("meditation_quotes", [])
    if meditation_quotes:
        return random.choice(meditation_quotes)
    return "No meditation quotes found."

# List of channels to send quotes to
channels_to_send = [
 #   "1328598213501911065", "1328598213501911064", "1328598213501911068", 
 #   "1329164837737205903", "1329165484398088254", "1329165305511153785",
 #   "1329166132678103213", "1329165078217621505", "1329165234010587226", 
 #   "1328598213501911069"
]  # Add your channel IDs here

# Task to send a random quote periodically
@tasks.loop(hours=3)  # Adjust time interval as needed (e.g., hours=1, minutes=30, etc.)
async def send_random_meditation_quote():
    # Get a different random quote for each channel
    random.shuffle(channels_to_send)  # Shuffle the list of channels to ensure randomness
    meditation_quotes = load_static_content().get("meditation_quotes", [])

    # Ensure there are enough quotes for each channel, loop through the quotes if needed
    for idx, channel_id in enumerate(channels_to_send):
        channel = bot.get_channel(int(channel_id))  # Ensure the channel ID is an integer
        if channel and meditation_quotes:
            # Send a different random quote to each channel
            quote = meditation_quotes[idx % len(meditation_quotes)]  # Cycle through quotes if necessary
            await channel.send(f"_**{quote}**_")
        else:
            print(f"Channel with ID {channel_id} not found or no quotes available.")
@bot.event
async def on_ready():
    activity = discord.Game(name="Recovery Support !help")  # Game type with no prefix like 'Playing'
    # Force the bot to cache all members
    await bot.guilds[0].chunk()  # Assumes the bot is in only one server
    await bot.change_presence(status=discord.Status.online, activity=activity)
    send_random_meditation_quote.start()  # Start the periodic task with the correct name
    logger.info(f"Bot is ready and logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Don't log bot's own messages
    logger.info(f"Sent message: '{message.content}' in channel: {message.channel.name}")
    await bot.process_commands(message)  # Ensure that other commands are processed


# Load static content (steps, traditions, prayers, etc.)
def load_static_content():
    with open("json/static.json", "r", encoding="utf-8") as f:
        return json.load(f)


# Load sponsor data
def load_sponsors():
    try:
        with open("json/sponsors.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to scrape "Just for Today" reading
def scrape_just_for_today():
    url = "https://www.jftna.org/jft/"
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)

        def get_text_safe(xpath):
            element = tree.xpath(xpath)
            return element[0].text_content().strip() if element else "N/A"

        date = get_text_safe("//h2")
        title = get_text_safe("//h1")
        page_number = get_text_safe("//td[contains(text(),'Page')]")
        quote = get_text_safe("//i")
        basic_text_page_number = get_text_safe("//tr[5]")
        basic_text_passage = get_text_safe("//tr[6]")
        passage = get_text_safe("//tr[7]")

        message = (
            f"`Just for Today N.A.`\n"
            f"-# {date}\n"
            f"# {title}\n"
            f"-# {page_number}\n\n"
            f"_{quote}_\n\n"
            f"**{basic_text_page_number}**:\n\n"
            f"**{basic_text_passage}**:\n\n"
            f"_**{passage}**_"
        )
        return message
    else:
        return "Failed to fetch Just for Today reading."

# Function to scrape the CoDA Weekly Reading
def scrape_coda_weekly_reading():
    url = "https://coda.org/weekly-reading/"
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)

        def get_text_safe(xpath):
            element = tree.xpath(xpath)
            return element[0].text_content().strip() if element else "N/A"

        page_title = get_text_safe("//h1[@class='pageTitle']")
        weekly_reading_title = get_text_safe("//h2[@class='entry-title']")
        content_paragraphs = tree.xpath("//div[contains(@class, 'pageContent')]//p")
        content = "\n\n".join(p.text_content().strip() for p in content_paragraphs if p.text_content().strip())

        message = (
            f"`CoDA Weekly Reading`\n"
            f"# {page_title}\n\n"
            f"> ## {weekly_reading_title}\n\n"
            f"{content}\n\n"
        )
        return message
    else:
        return "Failed to fetch CoDA Weekly Reading."



# Load daily reflections from the local JSON file
def fetch_daily_reflections():
    try:
        with open("json/reflections.json", "r", encoding="utf-8") as f:
            reflections = json.load(f)
            daily_reflections = {}

            for reflection in reflections:
                date_str = reflection.get("date")
                if date_str and "reflection" in reflection:
                    # Extract the reflection details
                    daily_reflections[date_str] = {
                        "title": reflection["title"],
                        "quote": reflection["quote"],
                        "source": reflection["source"],
                        "reflection": reflection["reflection"]
                    }
            return daily_reflections
    except FileNotFoundError:
        print("Daily reflections file not found.")
        return None

@bot.command(help="Displays the daily thought today")
async def twenty_four(ctx):
    # Fetch daily thoughts
    daily_thoughts = fetch_daily_thoughts()

    if daily_thoughts:
        # Get today's date based on the user's time zone
        local_date = get_local_date(ctx.author.name)

        if not local_date:
            await ctx.send("You haven't set your time zone yet. Use !time <timezone> to set it.")
            return

        # Retrieve the daily thought for the current date
        thought_data = daily_thoughts.get(local_date)

        if thought_data:
            # Format and display the daily thought message
            quote = thought_data["quote"]
            reflection = thought_data.get("reflection", "")
            prayer = thought_data.get("prayer", "")

            # Build the formatted thought message step by step
            formatted_thought = f">>> _**Daily Thought for**_   `{local_date}`\n\n"
            #formatted_thought += f"`{local_date}`\n"
            formatted_thought += f"{quote}\n\n"
            if reflection:
                formatted_thought += f"_**Meditation:**_\n{reflection}\n\n"
            if prayer:
                formatted_thought += f"_**Prayer:**_\n{prayer}\n"

            await ctx.send(formatted_thought)
        else:
            await ctx.send(f"No thought found for today ({local_date}).")
    else:
        await ctx.send("Could not fetch daily thoughts. Please try again later.")

# Command to set the time zone
@bot.command(help="Sets the user's time zone. The time zone should be a valid name (e.g., 'America/Phoenix').")
async def time(ctx, timezone: str):
    user_timezones = load_user_timezones()

    if timezone not in pytz.all_timezones:
        await ctx.send("Invalid time zone. Please provide a valid time zone name.")
        return

    user_timezones[ctx.author.name] = timezone
    save_user_timezones(user_timezones)

    await ctx.send(f"Time zone set to {timezone} for {ctx.author.name}")

# Get today's date based on the user's local time zone
def get_local_date(user):
    user_timezones = load_user_timezones()
    timezone = user_timezones.get(user)

    if not timezone:
        return None

    tz = pytz.timezone(timezone)
    local_time = datetime.now(tz)
    local_date = local_time.strftime("%B %d")  # e.g., "January 26"

    return local_date

# Modify the daily thought fetching function to use the local date
@bot.command(help="Displays the Daily Reflection for today")
async def daily(ctx):
    daily_reflections = fetch_daily_reflections()

    if daily_reflections:
        # Get today's date based on the user's time zone
        local_date = get_local_date(ctx.author.name)

        if not local_date:
            await ctx.send("You haven't set your time zone yet. Use !time <timezone> to set it.")
            return

        # Check if there's a reflection for today
        reflection_data = daily_reflections.get(local_date)

        if reflection_data:
            title = reflection_data["title"]
            quote = reflection_data["quote"]
            source = reflection_data["source"]
            reflection = reflection_data["reflection"]

            formatted_reflection = f"""
>>> ## {title}  
`{local_date}`  
 _**{quote}**_  

_**{source}**_  

```{reflection}```
            """
            await ctx.send(formatted_reflection)
        else:
            await ctx.send(f"No reflection found for today ({local_date}).")
    else:
        await ctx.send("Could not fetch daily reflections. Please try again later.")


# Command to list all prayers
@bot.command(help="Lists all available prayers. Use !prayer <number> to get a specific prayer.")
async def prayers(ctx):
    static_content = load_static_content()
    prayers = static_content.get("prayers", [])
    if prayers:
        prayer_list = "\n".join([
            f"{idx + 1}th Prayer: {prayer}"
            for idx, prayer in enumerate(prayers)
        ])
        await ctx.send(f"Available Prayers:\n>>> {prayer_list}")
    else:
        await ctx.send("No prayers found.")

# Command to display a specific prayer by key (e.g., "serenity", "3rd", etc.)
@bot.command("Displays a specific prayer by its name (e.g., 'serenity') or number (e.g., '3rd').")
async def prayer(ctx, prayer_name: str):
    static_content = load_static_content()
    prayers = static_content.get("prayers", {})

    prayer = prayers.get(prayer_name.lower())  # Get prayer by name (case insensitive)

    if prayer:
        await ctx.send(f"_**{prayer}**_")
    else:
        await ctx.send(f"Prayer '{prayer_name}' not found. Please enter a valid prayer name.")


# Command to display the 12 Steps
@bot.command(help="Lists the 12 Steps of the AA program.")
async def steps(ctx):
    """
    **!steps** - Displays the 12 Steps of the AA program.
    These steps are a core part of the recovery process and provide a structured approach for personal growth.
    """
    static_content = load_static_content()
    steps = static_content.get("steps", [])
    if steps:
        await ctx.send("\n".join(steps))
    else:
        await ctx.send("No steps found.")


# Command to display the Promises
@bot.command(help="Displays the Promises of the AA program.")
async def promises(ctx):
    static_content = load_static_content()
    promises = static_content.get("promises", [])
    if promises:
        await ctx.send("\n".join(promises))
    else:
        await ctx.send("No promises found.")


# Command to display the Preamble
@bot.command(help="Displays the Preamble of the AA program.")
async def preamble(ctx):
    static_content = load_static_content()
    preamble = static_content.get("preamble", "No preamble found.")
    await ctx.send(f"_**{preamble}**_")


# Command to display How It Works
@bot.command(help="Displays the 'How It Works' section, explaining the process of the AA program.")
async def how(ctx):
    # Load the static.json file
    with open("json/static.json", "r") as file:
        data = json.load(file)

    # Retrieve the content for each part
    howitworks_part1 = data.get("howitworks_part1", ["Content not available"])[0]
    howitworks_part2 = data.get("howitworks_part2", ["Content not available"])[0]
    howitworks_part3 = data.get("howitworks_part3", ["Content not available"])[0]

    # Replace '\n' with actual newlines in the content
    howitworks_part1 = howitworks_part1.replace("\\n", "\n")
    howitworks_part2 = howitworks_part2.replace("\\n", "\n")
    howitworks_part3 = howitworks_part3.replace("\\n", "\n")

    # Send each part as a separate message
    await ctx.send(howitworks_part1)
    await ctx.send(howitworks_part2)
    await ctx.send(howitworks_part3)

# Command to display the 12 Traditions
@bot.command(help="Displays the 12 Traditions of the AA program.")
async def traditions(ctx):
    static_content = load_static_content()
    traditions = static_content.get("traditions", [])
    if traditions:
        await ctx.send("\n".join(traditions))
    else:
        await ctx.send("No traditions found.")


# Command to display a random meditation quote
@bot.command(help="Displays a random meditation quote.")
async def meditation(ctx):
    static_content = load_static_content()
    meditation_quotes = static_content.get("meditation_quotes", [])
    if meditation_quotes:
        random_quote = random.choice(meditation_quotes)
        await ctx.send(f"_**{random_quote}**_")
    else:
        await ctx.send("No meditation quotes found.")

@bot.command(help="Adds the 'Sponsor' role to the user who invokes the command.")
async def sponsor_add(ctx):
    # Get the author (the user who invoked the command)
    member = ctx.author

    # Get the 'Sponsor' role
    sponsor_role = discord.utils.get(ctx.guild.roles, name="Sponsor")

    if not sponsor_role:
        await ctx.send("The 'Sponsor' role does not exist.")
        return

    # Add the 'Sponsor' role to the author
    await member.add_roles(sponsor_role)
    await ctx.send(f"Added the 'Sponsor' role to {member.name}.")
@bot.command(help="Removes the 'Sponsor' role from the user who invokes the command.")
async def sponsor_remove(ctx):
    # Get the author (the user who invoked the command)
    member = ctx.author

    # Get the 'Sponsor' role
    sponsor_role = discord.utils.get(ctx.guild.roles, name="Sponsor")

    if not sponsor_role:
        await ctx.send("The 'Sponsor' role does not exist.")
        return

    # Remove the 'Sponsor' role from the author
    if sponsor_role in member.roles:
        await member.remove_roles(sponsor_role)
        await ctx.send(f"Removed the 'Sponsor' role from {member.name}.")
    else:
        await ctx.send(f"{member.name} does not have the 'Sponsor' role.")

@bot.command(help="Lists all members who have the 'Sponsor' role.")
async def sponsorlist(ctx):
    # Fetch the 'Sponsor' role from the server
    sponsor_role = discord.utils.get(ctx.guild.roles, name="Sponsor")

    if not sponsor_role:
        await ctx.send("The 'Sponsor' role does not exist.")
        return

    print(f"Role found: {sponsor_role.name}, ID: {sponsor_role.id}")  # Log the role found

    sponsors = []

    # Loop through all members and check their roles
    for member in ctx.guild.members:
        print(f"Checking member: {member.name}, roles: {[role.name for role in member.roles]}")  # Log member's roles
        if sponsor_role in member.roles:
            sponsors.append(member.name)

    if sponsors:
        sponsors_list = "\n".join(sponsors)
        await ctx.send(f"Members with the 'Sponsor' role:\n{sponsors_list}")
    else:
        await ctx.send("No members found with the 'Sponsor' role.")

# Define the command that will post the messages
@bot.command()
async def jft(ctx):
    jft_message = scrape_just_for_today()
    if jft_message:
        await ctx.send(jft_message)
    else:
        await ctx.send("Failed to fetch Just for Today reading.")

@bot.command()
async def coda(ctx):
    coda_message = scrape_coda_weekly_reading()
    if coda_message:
        await ctx.send(coda_message)
    else:
        await ctx.send("Failed to fetch CoDA Weekly Reading.")

@bot.command()
async def purge(ctx, number: int):
    # Purge the specified number of messages in the channel
    deleted = await ctx.channel.purge(limit=number)

    # Create the dismissal button view
    view = DismissButton()

    # Send a message in the channel with the "dismiss" button only visible to the user who invoked the command
    msg = await ctx.send(f"{len(deleted)} messages have been purged.", view=view)

    # Make the button interaction ephemeral (only the invoker sees the button and response)
    await msg.delete(delay=10)  # Optionally, delete the message after 10 seconds (or another time)















# Run the bot
bot.run(config["bot_token"])
