import json
import pytz
from datetime import datetime
from nextcord.ext import commands

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Function to get the local date based on the user's time zone
    def get_local_date(self, user_id):
        user_timezones = self.load_user_timezones()
        timezone = user_timezones.get(str(user_id))  # Use user_id to ensure uniqueness

        if not timezone:
            return None

        tz = pytz.timezone(timezone)
        local_time = datetime.now(tz)
        local_date = local_time.strftime("%B %d")  # e.g., "January 26"

        return local_date

    # Function to load user timezones from the JSON file
    def load_user_timezones(self):
        try:
            with open("json/user_timezones.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print("Timezones file not found.")
            return {}

    # Function to fetch daily reflections from the local JSON file
    def fetch_daily_reflections(self):
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

    @commands.command(help="Displays the Daily Reflection for today")
    async def daily(self, ctx):
        daily_reflections = self.fetch_daily_reflections()

        if daily_reflections:
            # Retrieve the user's timezone using their user ID
            local_date = self.get_local_date(ctx.author.id)  # Use user ID for accurate lookup

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

    def fetch_daily_thoughts(self):
        try:
            with open("json/daily_thoughts.json", "r", encoding="utf-8") as f:
                daily_thoughts = json.load(f)  # Parse the JSON as a list of dictionaries
    
                daily_thoughts_data = {}
    
                for thought in daily_thoughts:
                    date_str = thought.get("date")
                    if date_str and "quote" in thought:
                        try:
                            parsed_date = datetime.strptime(date_str, "%B %d").strftime("%B %d")
                        except ValueError:
                            print(f"Invalid date format: {date_str}")
                            continue
                        
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

    @commands.command(help="Displays the daily thought today")
    async def twenty_four(self, ctx):
        daily_thoughts = self.fetch_daily_thoughts()

        if daily_thoughts:
            local_date = self.get_local_date(ctx.author.id)  # Use actual user ID for timezone

            if not local_date:
                await ctx.send("You haven't set your time zone yet. Use !time <timezone> to set it.")
                return

            thought_data = daily_thoughts.get(local_date)

            if thought_data:
                formatted_thought = f">>> _**Daily Thought for**_   `{local_date}`\n\n{thought_data['quote']}\n\n"
                if thought_data.get("reflection"):
                    formatted_thought += f"_**Meditation:**_\n{thought_data['reflection']}\n\n"
                if thought_data.get("prayer"):
                    formatted_thought += f"_**Prayer:**_\n{thought_data['prayer']}\n"

                await ctx.send(formatted_thought)
            else:
                await ctx.send(f"No thought found for today ({local_date}).")
        else:
            await ctx.send("Could not fetch daily thoughts. Please try again later.")


def setup(bot):
    bot.add_cog(Daily(bot))
