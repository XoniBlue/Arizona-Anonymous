from nextcord.ext import commands
import aiohttp
from lxml import html

class coda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Function to scrape the CoDA Weekly Reading using aiohttp for async HTTP requests
    async def scrape_coda_weekly_reading(self):
        url = "https://coda.org/weekly-reading/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()  # Get the content asynchronously
                    tree = html.fromstring(content)

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

    # Split the message into chunks of 2000 characters
    async def send_message_in_chunks(self, ctx, message):
        # Split the message into chunks of 2000 characters
        while len(message) > 2000:
            await ctx.send(message[:2000])  # Send the first 2000 characters
            message = message[2000:]  # Remove the first 2000 characters
        if message:  # Send any remaining message (less than or equal to 2000 characters)
            await ctx.send(message)

    @commands.command()
    async def coda(self, ctx):
        coda_message = await self.scrape_coda_weekly_reading()
        if coda_message:
            await self.send_message_in_chunks(ctx, coda_message)
        else:
            await ctx.send("Failed to fetch CoDA Weekly Reading.")

def setup(bot):
    bot.add_cog(coda(bot))
