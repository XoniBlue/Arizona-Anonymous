import threading
from flask import Flask
from nextcord.ext import commands

class Flask_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home)

        self.flask_thread = None
        self.running = False

    def home(self):
        return "Hello, Flask!"

    def run_flask(self):
        """Function to run Flask in a separate thread"""
        self.app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

    def stop_flask(self):
        """Stop Flask manually"""
        self.running = False
        if self.flask_thread:
            self.flask_thread.join()

    @commands.command()
    async def test_flask(self, ctx):
        # Test Flask function to ensure it's working
        await ctx.send("Flask is running.")

    @commands.Cog.listener()
    async def on_ready(self):
        """Run the Flask app when the bot is ready"""
        self.running = True
        self.flask_thread = threading.Thread(target=self.run_flask)
        self.flask_thread.daemon = True  # Ensure the thread ends when the bot shuts down
        self.flask_thread.start()

    @commands.Cog.listener()
    async def on_disconnect(self):
        """Stop Flask when the bot disconnects"""
        self.stop_flask()

def setup(bot):
    bot.add_cog(Flask_Cog(bot))
