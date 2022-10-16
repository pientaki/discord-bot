import random

import aiohttp
import discord
import giphy_client
from discord import app_commands
from discord.ext import commands
from giphy_client.rest import ApiException

kasuga = ['https://prtimes.jp/i/2610/255/resize/d2610-255-984823-4.jpg','https://news.mynavi.jp/article/20190428-816092/images/001.jpg','https://bunshun.jp/mwimgs/d/d/-/img_dd73c56ad1cb77d2cc8908c19fd104eb147104.jpg','https://www.sanspo.com/resizer/09u0U--V-d-TOXyDEbfEHpJiLGw=/360x240/filters:focal(786x960:796x970)/cloudfront-ap-northeast-1.images.arcpublishing.com/sankei/DRLINAMP6VIUPOJXADQGMLGIMQ.jpg','https://dogatch.jp/prod/kanren_news/20211122/f439b447540b8e6ef14282295cc7908d.jpg','https://dogatch.jp/prod/kanren_news/20220125/5ca0aadeda68dd31800ede03a3469dd8.jpg','https://www.sanspo.com/resizer/a5ba_8VIl4H6a1dQiiQQNL0NpPI=/360x240/filters:focal(293x372:303x382)/cloudfront-ap-northeast-1.images.arcpublishing.com/sankei/4BALJANZJJKWTH55SESRDFPK2Y.jpg','https://c799eb2b0cad47596bf7b1e050e83426.cdnext.stream.ne.jp/img/article/000/253/272/bf0d8c1ab11b1bec0b7ccbca29d5ecf920190504125911274.jpg','https://storage.nana-music.com/picture/426706-8a045b57-aa2a-4799-b6eb-82786e79cb1d-large.png']
rword = ["かすが","かす","カス","カスが","春日","春日俊彰"]

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Funny Cog is now ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for rword2 in rword:      
            if message.content == rword2:
                await message.channel.send(f'{random.choice(kasuga)}')                    

    @commands.hybrid_command(name="meme", description="💩ミームを投稿します💩", with_app_command=True)    
    async def meme(self, ctx: commands.Context):
        embed = discord.Embed(title="ミーム", color=discord.Color.from_rgb(255, 208, 0))
        async with aiohttp.ClientSession() as cs:
           async with cs.get('https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r:
               res = await r.json()
               embed.set_image(url=res['data']['children'][random.randint(0, 25)]['data']['url'])
               await ctx.send(embed=embed)

    @commands.hybrid_command(name="gif", description="gifを送信します💩", with_app_command=True)    
    @app_commands.describe(word="検索ワードを入力して下さい")
    async def gif(self, ctx: commands.Context, *, word: str):
        api_key="fVsOQXAeOFrJtB7o6X0gstsBQ6kpL2bY"
        api_instance = giphy_client.DefaultApi()
        try:
            api_response = api_instance.gifs_search_get(api_key, word, limit=5)
            lst = list(api_response.data)
            giff = random.choice(lst)
            await ctx.send(giff.embed_url)

        except ApiException as e:
            await ctx.send(e)

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
