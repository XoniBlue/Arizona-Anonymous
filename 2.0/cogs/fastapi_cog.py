from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from nextcord.ext import commands
import uvicorn
import threading

# Create FastAPI instance
app = FastAPI()

# Set up Jinja2 for template rendering
templates = Jinja2Templates(directory="templates")

# Define FastAPI routes
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/home")
async def home(request: Request):
    # Render the HTML template with context data
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello from FastAPI!"})

# Cog that contains your bot commands
class FastAPI_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test_api(self, ctx):
        # Test the FastAPI function to ensure it's working
        await ctx.send("FastAPI is running.")

def setup(bot):
    bot.add_cog(FastAPI_Cog(bot))

# Run FastAPI in a separate thread to avoid blocking the bot
if __name__ == "__main__":
    # Run FastAPI server outside of the Cog class to avoid threading conflicts
    uvicorn.run("cogs.fastapi_cog:app", host="0.0.0.0", port=8000, reload=True)
