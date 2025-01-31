import json
import random
import nextcord
from nextcord.ext import commands, tasks

class MeditationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels_to_send = [
            "1329168381680549898",  # Add your channel IDs here
        ]
        self.meditation_quotes = self.load_static_content().get("meditation_quotes", [])
        self.send_random_meditation_quote.start()  # Start the task when the cog is loaded

    # Load static content from a JSON file
    def load_static_content(self):
        try:
            with open("json/meditation.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Static content file not found.")
            return {}

    # Get a random meditation quote
    def get_random_meditation_quote(self):
        if self.meditation_quotes:
            return random.choice(self.meditation_quotes)
        return "No meditation quotes found."

    # Task to send a random quote periodically
    @tasks.loop(hours=3)  # Adjust time interval as needed (e.g., hours=1, minutes=30, etc.)
    async def send_random_meditation_quote(self):
        random.shuffle(self.channels_to_send)  # Shuffle the list of channels to ensure randomness

        # Ensure there are enough quotes for each channel, loop through the quotes if needed
        for idx, channel_id in enumerate(self.channels_to_send):
            channel = self.bot.get_channel(int(channel_id))  # Ensure the channel ID is an integer
            if channel and self.meditation_quotes:
                quote = self.meditation_quotes[idx % len(self.meditation_quotes)]  # Cycle through quotes if necessary
                await channel.send(f"_**{quote}**_")
            else:
                print(f"Channel with ID {channel_id} not found or no quotes available.")

    # Command to display a random meditation quote
    @commands.command(help="Displays a random meditation quote.")
    async def meditation(self, ctx):
        if self.meditation_quotes:
            random_quote = random.choice(self.meditation_quotes)
            await ctx.send(f"_**{random_quote}**_")
        else:
            await ctx.send("No meditation quotes found.")

    # Event triggered when the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        # Set the bot's presence (optional, if you want a custom status message)
        activity = nextcord.Game(name="Recovery Support !help")  # Game type with no prefix like 'Playing'
        await self.bot.change_presence(status=nextcord.Status.online, activity=activity)
        print(f"Bot is ready and logged in as {self.bot.user}")

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(MeditationCog(bot))
