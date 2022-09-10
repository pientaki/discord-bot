import discord
from discord.ext import commands
from discord import app_commands
import requests
import json

class Ai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("AI Cog is now ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            pass
        elif self.bot.user in message.mentions:       
            words = message.content
            rewords = words[22:]
            headers = {"Content-Type": "application/json"}
            payload = {"api_key":"c65aa7c6-abf2-4648-b063-5f12ec54ab2817fef5aef5f309","agent_id":"c2053c64-9d63-4f6a-acec-843634affc7917fef588da8178","utterance": rewords,"uid":"mebo.testtesttest001"}
            url = 'https://api-mebo.dev/api'
            r = requests.post(url=url, headers=headers, data=json.dumps(payload))
            text = r.text
            data = json.loads(text)
            await message.channel.send('{}'.format(data['bestResponse']['utterance']))

async def setup(bot: commands.Bot):
    await bot.add_cog(Ai(bot))