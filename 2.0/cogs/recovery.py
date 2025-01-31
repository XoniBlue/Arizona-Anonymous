import json
import nextcord
from nextcord.ext import commands

class RecoveryInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_static_content(self):
        """Load static content from JSON file."""
        try:
            with open("json/static.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: 'static.json' file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Failed to decode the JSON data.")
            return {}

    @commands.command(help="Lists all available prayers. Use !prayer <number> to get a specific prayer.")
    async def prayers(self, ctx):
        static_content = self.load_static_content()
        prayers = static_content.get("prayers", [])
        if prayers:
            prayer_list = "\n".join([f"{idx + 1}th Prayer: {prayer}" for idx, prayer in enumerate(prayers)])
            await ctx.send(f"Available Prayers:\n>>> {prayer_list}")
        else:
            await ctx.send("No prayers found.")

    @commands.command(help="Displays a specific prayer by its name (e.g., 'serenity') or number (e.g., '3rd').")
    async def prayer(self, ctx, prayer_name: str):
        static_content = self.load_static_content()
        prayers = static_content.get("prayers", {})

        prayer = prayers.get(prayer_name.lower())  # Get prayer by name (case insensitive)
        if prayer:
            await ctx.send(f"_**{prayer}**_")
        else:
            await ctx.send(f"Prayer '{prayer_name}' not found. Please enter a valid prayer name.")

    @commands.command(help="Lists the 12 Steps of the AA program.")
    async def steps(self, ctx):
        static_content = self.load_static_content()
        steps = static_content.get("steps", [])
        if steps:
            await ctx.send("\n".join(steps))
        else:
            await ctx.send("No steps found.")

    @commands.command(help="Displays the Promises of the AA program.")
    async def promises(self, ctx):
        static_content = self.load_static_content()
        promises = static_content.get("promises", [])
        if promises:
            await ctx.send("\n".join(promises))
        else:
            await ctx.send("No promises found.")

    @commands.command(help="Displays the Preamble of the AA program.")
    async def preamble(self, ctx):
        static_content = self.load_static_content()
        preamble = static_content.get("preamble", "No preamble found.")
        await ctx.send(f"_**{preamble}**_")

    @commands.command(help="Displays the 'How It Works' section, explaining the process of the AA program.")
    async def how(self, ctx):
        static_content = self.load_static_content()
        howitworks_part1 = static_content.get("howitworks_part1", ["Content not available"])[0]
        howitworks_part2 = static_content.get("howitworks_part2", ["Content not available"])[0]
        howitworks_part3 = static_content.get("howitworks_part3", ["Content not available"])[0]

        # Replace '\n' with actual newlines in the content
        howitworks_part1 = howitworks_part1.replace("\\n", "\n")
        howitworks_part2 = howitworks_part2.replace("\\n", "\n")
        howitworks_part3 = howitworks_part3.replace("\\n", "\n")

        # Send each part as a separate message
        await ctx.send(howitworks_part1)
        await ctx.send(howitworks_part2)
        await ctx.send(howitworks_part3)

    @commands.command(help="Displays the 12 Traditions of the AA program.")
    async def traditions(self, ctx):
        static_content = self.load_static_content()
        traditions = static_content.get("traditions", [])
        if traditions:
            await ctx.send("\n".join(traditions))
        else:
            await ctx.send("No traditions found.")

def setup(bot):
    bot.add_cog(RecoveryInfo(bot))
