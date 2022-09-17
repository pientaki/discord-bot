import discord
from discord.ext import commands
from discord import app_commands
import datetime
from googletrans import Translator
import googletrans
from googlesearch import search
from urllib import parse
from googleapiclient.discovery import build
import random
import wikipedia
#from selenium import webdriver
import requests
import time

translator = Translator()
api_key = "AIzaSyBJmDRfabTIgyx6as6WrCPalj1w4C0AYaE"
weather_api_key = "9249796b3e638520a7b1f44a4830eb02"
base_url = "http://api.openweathermap.org/data/2.5/weather?"

class Search(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Search Cog is now ready!")

    @commands.hybrid_command(name="translate", description="翻訳します", with_app_command=True)    
    @app_commands.describe(lang_to="翻訳したい言語を入力(例. en,ja,hi...)", text = "翻訳したい内容を入力して下さい")
    async def translate(self, ctx: commands.Context, lang_to: str, text: str):
        lang_to = lang_to.lower()
        if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
            raise commands.BadArgument("!!ERROR!!")
            
        translator = googletrans.Translator()
        text_translated = translator.translate(text, dest=lang_to).text
        await ctx.send(text_translated)

    @commands.hybrid_command(name="translate-language", description="翻訳言語一覧を表示します", with_app_command=True)    
    async def lang(self, ctx: commands.Context):
        embed = discord.Embed(title="翻訳言語一覧",color=discord.Color.blurple())
        embed.description=(f"**Japanese :** ja \n"f"**English :** en \n"f"**Hindi :** hi\n\n"f"**:united_nations: その他**\n" "https://py-googletrans.readthedocs.io/en/latest/")
        await ctx.send(embed=embed)

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

    @commands.hybrid_command(name="googlesearch", description="Googleで検索します(上位5件分)", with_app_command=True)    
    @app_commands.describe(word="検索ワードを入力して下さい")
    async def gserch(self, ctx: commands.Context, word: str):
        kensaku = word
        for url in search(kensaku, lang="jp",num_results = 5):
            await ctx.send(url)

    @commands.hybrid_command(name="search", description="インターネットの検索結果のリンクを生成します", with_app_command=True)    
    @app_commands.describe(word="検索ワードを入力して下さい")
    async def isearch(self, ctx: commands.Context, *, word: str):
        param = parse.urlencode({"q": word})
        await ctx.send(
            f" `{word}` についての検索結果は以下の通りです。",
            view=discord.ui.View(
                discord.ui.Button(
                    label="Google", url=f"https://www.google.com/search?{param}"
                ),
                discord.ui.Button(
                    label="Bing", url=f"https://www.bing.com/search?{param}"
                ),
                discord.ui.Button(
                    label="DuckDuckGo", url=f"https://www.duckduckgo.com/?{param}"
                ),
            ),
        )

    @commands.hybrid_command(name="imagesearch", description="画像を検索します", with_app_command=True)
    @app_commands.rename(search="検索キーワード")    
    @app_commands.describe(search="検索したい画像名を入力して下さい")
    async def image(self, ctx: commands.Context, *, search: str):
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        ran = random.randint(0, 9)
        resource = build("customsearch", "v1", developerKey=api_key).cse()
        result = resource.list(
            q=f"{search}", cx="2dde91b36931db923", searchType="image"
        ).execute()
        url = result["items"][ran]["link"]
        embed = discord.Embed(title=f" `{search}` の画像", timestamp=datetime.datetime.now(JST))
        embed.set_image(url=url)
        embed.set_footer(text=f"{ctx.author.name}のリクエスト")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="wiki", description="wikipediaで検索します", with_app_command=True)
    @app_commands.rename(search="検索キーワード")    
    @app_commands.describe(search="検索ワードを入力して下さい")
    async def wiki(self, ctx: commands.Context, search: str):
        wikipedia.set_lang("ja")
        try:
            embed = discord.Embed(title=f"{search}")
            embed.add_field(name="概要", value=wikipedia.summary(search))
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Wikipedia-logo-v2-en.svg/1784px-Wikipedia-logo-v2-en.svg.png")
            await ctx.send(embed=embed)
        except wikipedia.exceptions.DisambiguationError as e:
            embed = discord.Embed(title="検索失敗", description="下の候補から選んで下さい")
            embed.add_field(name="候補", value=e)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Wikipedia-logo-v2-en.svg/1784px-Wikipedia-logo-v2-en.svg.png")
            await ctx.send(embed=embed)
        except wikipedia.exceptions.PageError:
            await ctx.send(f"{search}の結果が見つかりませんでした")

    #@commands.hybrid_command(name="screenshot", description="ネット上のページのスクリーンショットを撮影します", with_app_command=True)    
    #@app_commands.describe(word="URLか検索したいページのキーワードを入力して下さい")
    #async def ss(self, ctx: commands.Context, word: str):
        #await ctx.defer()
        #try:
            #options = webdriver.ChromeOptions()
            #options.add_argument('--headless')
            #options.add_argument('--disable-gpu')
            #options.add_argument('--no-sandbox')
            #options.add_argument('--disable-dev-shm-usage')
            #options.add_argument('--remote-debugging-port=9222')
            #options.add_experimental_option('excludeSwitches', ['enable-logging'])
            #browser = webdriver.Chrome("chromedriver.exe", options=options)
            #browser.set_window_size(950, 800)

            #if not 'http' in str(word):
                #kensaku = word
                #for url in search(kensaku, lang="jp",num_results = 1):
                    #browser.get(url)
                    #browser.get_screenshot_as_file('screenshot.png')

                    #file = discord.File('screenshot.png', filename='image.png')
                    #embed = discord.Embed(title=f"{url}")
                    #embed.set_image(url='attachment://image.png')
                    #await ctx.send(file=file, embed=embed)
                    #browser.quit()

            #else:
                #browser.get(word)
                #browser.get_screenshot_as_file('screenshot.png')

                #file = discord.File('screenshot.png', filename='image.png')

                
                #embed = discord.Embed(title=f"{word}")
                #embed.set_image(url='attachment://image.png')
                #await ctx.send(file=file, embed=embed)
                #browser.quit()

        #except Exception as e:
            #await ctx.send("error")    

    @commands.hybrid_command(name="weather", description="天気を表示します", with_app_command=True)    
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

    #@commands.hybrid_command(name="covid", description="大阪府の新型コロナウイルス新規感染者数を表示します", with_app_command=True)    
    #async def covid(self, ctx: commands.Context):
        #await ctx.defer()
        #async with ctx.typing():
            #options = webdriver.ChromeOptions()
            #options.add_argument('--headless')
            #options.add_argument('--disable-gpu')
            #options.add_argument('--no-sandbox')
            #options.add_argument('--disable-dev-shm-usage')
            #options.add_argument('--remote-debugging-port=9222')
            #options.add_experimental_option('excludeSwitches', ['enable-logging'])
            #browser = webdriver.Chrome("chromedriver.exe", options=options)
            #browser.set_window_size(950, 800)
           
            #browser.get('https://www.watch.impress.co.jp/extra/covid19/?pref=27') 
            #data = browser.find_elements_by_class_name("extra-wrap")
            #text = data[0].text
            #time.sleep(5)
            #browser.quit()

            #embed=discord.Embed(title="大阪府新型コロナウイルス感染者数", color=discord.Color.from_rgb(255, 0, 0))
            #embed.set_thumbnail(url="https://www.apsf.org/wp-content/uploads/newsletters/2020/3502/coronavirus-covid-19.png")
            #embed.description=(text)
            #await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Search(bot))