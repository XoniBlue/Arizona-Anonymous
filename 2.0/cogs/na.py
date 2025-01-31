from nextcord.ext import commands
import requests
from lxml import html

class na(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        

    # Function to scrape "Just for Today" reading
    def scrape_just_for_today(self):
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
            
            #message formatting
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

    # Define the command that will post the messages
    @commands.command()
    async def jft(self, ctx):
        jft_message = self.scrape_just_for_today()
        if jft_message:
            await ctx.send(jft_message)
        else:
            await ctx.send("Failed to fetch Just for Today reading.")
    
def setup(bot):
    bot.add_cog(na(bot))