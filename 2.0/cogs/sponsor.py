import json
import nextcord
from nextcord.ext import commands

class Sponsor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sponsor_role_name = "Sponsor"  # Name of the role
        self.sponsors_file = "json/sponsors.json"  # Path to the sponsors data file

    # Load sponsor data from the JSON file
    def load_sponsors(self):
        try:
            with open(self.sponsors_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    # Command to add the 'Sponsor' role to the user invoking the command
    @commands.command(help="Adds the 'Sponsor' role to the user who invokes the command.")
    async def sponsor_add(self, ctx):
        member = ctx.author
        sponsor_role = nextcord.utils.get(ctx.guild.roles, name=self.sponsor_role_name)

        if not sponsor_role:
            await ctx.send("The 'Sponsor' role does not exist.")
            return

        await member.add_roles(sponsor_role)
        await ctx.send(f"Added the 'Sponsor' role to {member.name}.")

    # Command to remove the 'Sponsor' role from the user invoking the command
    @commands.command(help="Removes the 'Sponsor' role from the user who invokes the command.")
    async def sponsor_remove(self, ctx):
        member = ctx.author
        sponsor_role = nextcord.utils.get(ctx.guild.roles, name=self.sponsor_role_name)

        if not sponsor_role:
            await ctx.send("The 'Sponsor' role does not exist.")
            return

        if sponsor_role in member.roles:
            await member.remove_roles(sponsor_role)
            await ctx.send(f"Removed the 'Sponsor' role from {member.name}.")
        else:
            await ctx.send(f"{member.name} does not have the 'Sponsor' role.")

    # Command to list all members who have the 'Sponsor' role and their availability status
    @commands.command(help="Lists all members who have the 'Sponsor' role and their availability status.")
    async def sponsorlist(self, ctx):
        sponsor_role = nextcord.utils.get(ctx.guild.roles, name=self.sponsor_role_name)

        if not sponsor_role:
            await ctx.send("The 'Sponsor' role does not exist.")
            return

        sponsors = []
        sponsors_data = self.load_sponsors()

        # Loop through all members and check their roles
        for member in ctx.guild.members:
            if sponsor_role in member.roles:
                # Get the availability status for each sponsor
                status = sponsors_data.get(str(member.id), {}).get("status", "No status set")
                sponsors.append(f"{member.name} - {status}")

        if sponsors:
            sponsors_list = "\n".join(sponsors)
            await ctx.send(f"Members with the 'Sponsor' role and their availability status:\n{sponsors_list}")
        else:
            await ctx.send("No members found with the 'Sponsor' role.")

    # Command to check or update the availability status of the invoking sponsor
    @commands.command(help="Sets or checks the availability status of a sponsor.")
    async def sponsor_status(self, ctx, status: str = None):
        sponsor_role = nextcord.utils.get(ctx.guild.roles, name=self.sponsor_role_name)

        if not sponsor_role:
            await ctx.send("The 'Sponsor' role does not exist.")
            return

        member = ctx.author

        # Check if the member has the 'Sponsor' role
        if sponsor_role not in member.roles:
            await ctx.send("You don't have the 'Sponsor' role, so no status was changed.")
            return

        if status is None:
            # If no status is provided, show the current status
            sponsors_data = self.load_sponsors()
            current_status = sponsors_data.get(str(member.id), {}).get("status", "No status set")
            await ctx.send(f"Your current status is: {current_status}")
        else:
            # Set or update the availability status
            sponsors_data = self.load_sponsors()
            sponsors_data[str(member.id)] = {"status": status}

            # Save the updated data back to the JSON file
            with open(self.sponsors_file, "w", encoding="utf-8") as f:
                json.dump(sponsors_data, f, indent=4)

            await ctx.send(f"Your status has been set to: {status}")

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(Sponsor(bot))
