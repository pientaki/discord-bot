import datetime
import random
import os
from urllib import parse

import discord
import googletrans
#from selenium import webdriver
import requests
import wikipedia
from discord import app_commands
from discord.ext import commands
from googleapiclient.discovery import build
from googlesearch import search
from googletrans import Translator
from data.lg import lg

translator = Translator()
g_api_key = os.environ["g_api_key"]
weather_api_key = os.environ["weather_api_key"]
base_url = "http://api.openweathermap.org/data/2.5/weather?"

class Wikiview(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        
        url = url
        self.add_item(discord.ui.Button(label='リンク', url=url))


class Search(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Search Cog is now ready!")

    @commands.hybrid_command(name="translate", description="翻訳します", with_app_command=True)    
    @app_commands.describe(lang_to="翻訳したい言語を選択して下さい", text = "翻訳したい内容を入力して下さい")
    async def translate(self, ctx: commands.Context, lang_to: lg, text: str):
        lang_to = lang_to.lower()
        if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
            raise commands.BadArgument("!!ERROR!!")
            
        translator = googletrans.Translator()
        text_translated = translator.translate(text, dest=lang_to).text
        await ctx.send(text_translated)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.count == 1:
            if str(reaction.emoji) == "🇮🇳":
                translator = Translator()
                country = translator.detect(text=reaction.message.content)
                trans_en = translator.translate(text=reaction.message.content,  src=country.lang, dest='hi')
                await reaction.message.channel.send(trans_en.text)

            if str(reaction.emoji) == "🇯🇵":
                translator = Translator()
                country = translator.detect(text=reaction.message.content)
                trans_en = translator.translate(text=reaction.message.content,  src=country.lang, dest='ja')
                await reaction.message.channel.send(trans_en.text)

            if str(reaction.emoji) == "🇺🇸":
                translator = Translator()
                country = translator.detect(text=reaction.message.content)
                trans_en = translator.translate(text=reaction.message.content,  src=country.lang, dest='en')
                await reaction.message.channel.send(trans_en.text)

    @commands.hybrid_group()
    async def search(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Search commands")

    @search.command(name="google", description="Googleで検索します(上位5件分)", with_app_command=True)    
    @app_commands.describe(word="検索ワードを入力して下さい")
    async def gserch(self, ctx: commands.Context, word: str):
        kensaku = word
        for url in search(kensaku, lang="jp",num_results = 5):
            await ctx.send(url)

    @search.command(name="image", description="画像を検索します", with_app_command=True)
    @app_commands.rename(search="検索ワード")   
    @app_commands.describe(search="検索したい画像名を入力して下さい")
    async def image(self, ctx: commands.Context, *, search: str):
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        ran = random.randint(0, 9)
        resource = build("customsearch", "v1", developerKey=g_api_key).cse()
        result = resource.list(
            q=f"{search}", cx="2dde91b36931db923", searchType="image"
        ).execute()
        url = result["items"][ran]["link"]
        embed = discord.Embed(title=f" `{search}` の画像", timestamp=datetime.datetime.now(JST))
        embed.set_image(url=url)
        embed.set_footer(text=f"{ctx.author.name}のリクエスト")
        await ctx.send(embed=embed)

    @search.command(name="wiki", description="wikipediaで検索します", with_app_command=True)
    @app_commands.rename(search="検索ワード")    
    @app_commands.describe(search="検索ワードを入力して下さい")
    async def wiki(self, ctx: commands.Context, search: str):
        await ctx.defer()
        wikipedia.set_lang("ja")
        wi = wikipedia.page(search)
        url = wi.url
        try:
            embed = discord.Embed(title=f"{search}")
            embed.add_field(name="概要", value=wikipedia.summary(search))
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Wikipedia-logo-v2-en.svg/1784px-Wikipedia-logo-v2-en.svg.png")
            await ctx.send(embed=embed, view=Wikiview(url))
        except wikipedia.exceptions.DisambiguationError as e:
            embed = discord.Embed(title="検索失敗", description="下の候補から選んで下さい")
            embed.add_field(name="候補", value=e)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Wikipedia-logo-v2-en.svg/1784px-Wikipedia-logo-v2-en.svg.png")
            await ctx.send(embed=embed)
        except wikipedia.exceptions.PageError:
            await ctx.send(f"{search}の結果が見つかりませんでした")

    '''@commands.hybrid_command(name="screenshot", description="ネット上のページのスクリーンショットを撮影します", with_app_command=True)    
    @app_commands.describe(word="URLか検索したいページのキーワードを入力して下さい")
    async def ss(self, ctx: commands.Context, word: str):
        await ctx.defer()
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--remote-debugging-port=9222')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            browser = webdriver.Chrome("chromedriver.exe", options=options)
            browser.set_window_size(950, 800)

            if not 'http' in str(word):
                kensaku = word
                for url in search(kensaku, lang="jp",num_results = 1):
                    browser.get(url)
                    browser.get_screenshot_as_file('screenshot.png')

                    file = discord.File('screenshot.png', filename='image.png')
                    embed = discord.Embed(title=f"{url}")
                    embed.set_image(url='attachment://image.png')
                    await ctx.send(file=file, embed=embed)
                    browser.quit()

            else:
                browser.get(word)
                browser.get_screenshot_as_file('screenshot.png')

                file = discord.File('screenshot.png', filename='image.png')

                
                embed = discord.Embed(title=f"{word}")
                embed.set_image(url='attachment://image.png')
                await ctx.send(file=file, embed=embed)
                browser.quit()

        except Exception as e:
            await ctx.send("error")'''    

    @search.command(name="weather", description="天気を表示します", with_app_command=True)    
    @app_commands.describe(city="地名を入力して下さい(英語)")
    async def weather(self, ctx: commands.Context, city: str):
        city_name = city
        complete_url = base_url + "appid=" + weather_api_key + "&q=" + city_name + "&lang="+ "ja"
        response = requests.get(complete_url)
        x = response.json()

        if x["cod"] != "404":
            async with ctx.typing():
                y = x["main"]
                current_temperature = y["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                icon = z[0]["icon"]
                w = x["wind"]
                wind_speed = w["speed"]
                wind_direction = w["deg"]
                c = x["clouds"]
                cloud_description = c["all"]
                embed = discord.Embed(title=f"{city_name}の天気",
                                color=ctx.guild.me.top_role.color)
                embed.add_field(name="詳細", value=f"**{weather_description}**", inline=False)
                embed.add_field(name="気温(C)", value=f"**{current_temperature_celsiuis}°C**")
                embed.add_field(name="湿度(%)", value=f"**{current_humidity}%**")
                embed.add_field(name="気圧(hPa)", value=f"**{current_pressure}hPa**")
                embed.add_field(name="風速", value=f"**{wind_speed}m/s**")
                embed.add_field(name="風向き", value=f"**{wind_direction}**")
                embed.add_field(name="曇り率", value=f"**{cloud_description}%**", inline=False)
                embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
                embed.set_footer(text=f"{ctx.author.name}のリクエスト")
                await ctx.send(embed=embed)        
        else:
            await ctx.send("場所が見つかりません")

    '''

    @commands.hybrid_command(name="covid", description="大阪府の新型コロナウイルス新規感染者数を表示します", with_app_command=True)    
    async def covid(self, ctx: commands.Context):
        await ctx.defer()
        async with ctx.typing():
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--remote-debugging-port=9222')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            browser = webdriver.Chrome("chromedriver.exe", options=options)
            browser.set_window_size(950, 800)
           
            browser.get('https://www.watch.impress.co.jp/extra/covid19/?pref=27') 
            data = browser.find_elements_by_class_name("extra-wrap")
            text = data[0].text
            time.sleep(5)
            browser.quit()

            embed=discord.Embed(title="大阪府新型コロナウイルス感染者数", color=discord.Color.from_rgb(255, 0, 0))
            embed.set_thumbnail(url="https://www.apsf.org/wp-content/uploads/newsletters/2020/3502/coronavirus-covid-19.png")
            embed.description=(text)
            await ctx.send(embed=embed)

    '''

    @commands.hybrid_command(name="embed", description="埋め込みメッセージを作成します", with_app_command=True)
    @app_commands.rename(title="タイトル", description="内容")    
    @app_commands.describe(title="タイトルを入力して下さい", description="内容を入力して下さい")
    async def make_embed(self, ctx: commands.Context, title: str, description: str):
        embed=discord.Embed(title=title, description=description, color=ctx.author.color)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Search(bot))