import pytz
from datetime import datetime
import json
from nextcord.ext import commands

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Load the user's time zone from the JSON file
    def load_user_timezones(self):
        try:
            with open("json/user_timezones.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print("File not found. Returning empty dictionary.")
            return {}

    # Save the user's time zone to the JSON file
    def save_user_timezones(self, user_timezones):
        with open("json/config.json", "w", encoding="utf-8") as f:
            json.dump(user_timezones, f, indent=4)

    # Command to set the time zone
    @commands.command(help="Sets the user's time zone. The time zone should be a valid name (e.g., 'America/Phoenix').")
    async def time(self, ctx, timezone: str):
        user_timezones = self.load_user_timezones()

        if timezone not in pytz.all_timezones:
            await ctx.send("Invalid time zone. Please provide a valid time zone name.")
            return

        # Use user ID instead of name for more reliable data handling
        user_id = str(ctx.author.id)

        # Check if the user has an existing time zone, and update if necessary
        if user_id in user_timezones:
            old_timezone = user_timezones[user_id]
            if old_timezone != timezone:
                user_timezones[user_id] = timezone
                await ctx.send(f"Time zone updated from {old_timezone} to {timezone} for {ctx.author.name}")
            else:
                await ctx.send(f"Your time zone is already set to {timezone}.")
        else:
            user_timezones[user_id] = timezone
            await ctx.send(f"Time zone set to {timezone} for {ctx.author.name}")

        self.save_user_timezones(user_timezones)

# Set up the cog
def setup(bot):
    bot.add_cog(Utils(bot))
