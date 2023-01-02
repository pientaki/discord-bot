import os
import pathlib
from enum import Enum

import discord
import requests
import ujson as json
from discord import app_commands
from discord.ext import commands


class Styles(Enum):
    synthwave = 1
    ukiyoe = 2
    steampunk = 4
    fantasy_art = 5
    vibrant = 6
    hd = 7
    pastel = 8
    psychic = 9
    dark_fantasy = 10
    mystical = 11
    festive = 12
    baroque = 13
    etching = 14
    sdali = 15
    wuhtercuhler = 16
    provenance = 17
    rose_gold = 18
    moonwalker = 19
    blacklight = 20
    psychedelic = 21
    ghibil = 22
    surreal = 23
    no_style = 3
    radioactive = 27
    arcane = 34


async def gen_image(prompt: str, style):
    with requests.Session() as session:

        get_token = requests.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw",
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, "
                              "like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "content-type": "application/json",
                "x-client-version": "Firefox/JsCore/9.1.2/FirebaseCore-web",
                "Origin": "https://app.wombo.art",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "TE": "trailers"
            }, json={
                "returnSecureToken": "true"
            }).json()
        id_token = get_token["idToken"]

        get_id = requests.post("https://paint.api.wombo.ai/api/tasks", headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://app.wombo.art/",
            "Authorization": f"bearer {id_token}",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://app.wombo.art",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }, json={
            "premium": False
        }).json()

        task_id = get_id["id"]

        initCreateTask = requests.put(f"https://paint.api.wombo.ai/api/tasks/{task_id}", headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://app.wombo.art/",
            "Authorization": f"bearer {id_token}",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://app.wombo.art",
            "DNT": "1",
            "Connection": "keep-alive",
            "Cookie": "_ga_BRH9PT4RKM=GS1.1.1644347760.1.0.1644347820.0; _ga=GA1.1.1610806426.1644347761",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }, json={
            "input_spec": {
                "prompt": prompt,
                "style": style.value,
                "display_freq": 10
            }
        })

    while True:
        r = session.get(f"https://paint.api.wombo.ai/api/tasks/{task_id}", headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://app.wombo.art/",
            "Authorization": f"bearer {id_token}",
            "DNT": "1",
            "Connection": "keep-alive",
            "Cookie": "_ga_BRH9PT4RKM=GS1.1.1644347760.1.0.1644347820.0; _ga=GA1.1.1610806426.1644347761",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        })
        data = r.json()
        if "state" in data:
            state = data["state"]

            if state == "completed":
                break
            if state == "failed":
                print(data)

                raise RuntimeError(data)

        if not ("state" in data):
            return

    finishedImage_url = data["result"]["final"]
    return finishedImage_url


class Wombo(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Wombo Cog is now ready!")


    @commands.hybrid_command(name="aidrow",with_app_command = True, description="AIがお絵描きします")
    @app_commands.describe(prompt="AIに描かせるテーマを入力してください", style="絵のスタイルを選択して下さい")      
    async def art(self, ctx: commands.Context, prompt: str, style: Styles):
        await ctx.defer() 
        c = await gen_image(prompt, style)

        img_file = f"{prompt}_{style.name}.png"

        with open(img_file, "wb") as file:
            file.write(requests.get(c).content)
            file.close()

        path = pathlib.Path(img_file)
        if path.exists():
            await ctx.send(file=discord.File(img_file))
            for img_file in os.listdir("./"):
                if img_file.endswith(".png"):
                    os.remove(img_file)


async def setup(bot: commands.Bot):  
    await bot.add_cog(Wombo(bot))  