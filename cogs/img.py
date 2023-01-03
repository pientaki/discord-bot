import os
import discord
from discord.ext import commands
from discord import app_commands
import cv2
import requests
import shutil
from PIL import Image, ImageDraw , ImageFilter
from io import BytesIO

HAAR_FILE = "./data/haarcascade_frontalface_default.xml"
IMG_PATH = "./img/"
IMG_SIZE = (128, 128)

def mosaic(img, scale=0.1):
    h, w = img.shape[:2] 

    dst = cv2.resize(
        img, dsize=None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST
    )

    dst = cv2.resize(dst, dsize=(w, h), interpolation=cv2.INTER_NEAREST)

    return dst

class Image(commands.Cog):
    def __init__(self, bot: commands.Bot):        
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Image Cog is now ready!")

    @commands.hybrid_group()
    async def image(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Image commands")

    @image.command(name="mono",with_app_command = True, description="アバターを白黒画像に変換します")
    @app_commands.rename(member="メンバー")    
    @app_commands.describe(member="メンバーを選択して下さい")
    async def mono(self, ctx: commands.Context, member: discord.Member = None):
        if member == None:
            member = ctx.author

        data = BytesIO(await member.display_avatar.read())
        pfp = Image.open(data)

        nwpfp = pfp.convert("L")

        nwpfp.save("./img/avater.jpg")

        await ctx.send(file=discord.File("./img/avater.jpg"))
        os.remove("./img/avater.jpg")

    @image.command(name="monochrome",with_app_command = True, description="白黒画像を生成します")
    @app_commands.rename(img="画像")    
    @app_commands.describe(img="対応フォーマットは png jpg です")
    async def imgmono(self, ctx: commands.Context, img: discord.Attachment):
       

        data = BytesIO(await img.read())
        pfp = Image.open(data)

        nwpfp = pfp.convert("L")

        nwpfp.save("./img/dc.jpg")

        await ctx.send(file=discord.File("./img/dc.jpg"))
        os.remove("./img/dc.jpg")

    @image.command(name="gif",with_app_command = True, description="gifを生成します")
    @app_commands.rename(img="画像")    
    @app_commands.describe(img="対応フォーマットは png jpg です")
    async def mozagif(self, ctx: commands.Context, img: discord.Attachment):
        await ctx.defer()
       

        data = BytesIO(await img.read())
        pfp = Image.open(data)

        pfp_list = []

        for i in range(35,0,-1):    
            pfp_r = pfp.filter(ImageFilter.GaussianBlur(i))
            pfp_list.append(pfp_r)

        pfp_list[0].save('./img/blur.gif', save_all=True, append_images=pfp_list[1:], optimize=True, duration=200, loop=0)  
    
        await ctx.send(file=discord.File("./img/blur.gif"))
        os.remove("./img/blur.gif")

    @image.command(name="mosaic",with_app_command = True, description="画像から人の顔を検出してモザイクをかけます")
    @app_commands.rename(shashin="画像")    
    @app_commands.describe(shashin="対応フォーマットは png jpg です")
    async def facecut(self, ctx: commands.Context, shashin: discord.Attachment):
        await ctx.defer()

        cascade = cv2.CascadeClassifier(HAAR_FILE)

        data = shashin.url

        file_name = data.rsplit("/", 1)[1]
        rst = requests.get(data, stream = True)
        
        open_file = open(IMG_PATH + file_name, "wb")

        shutil.copyfileobj(rst.raw, open_file)
        open_file.close()
    
        img = cv2.imread(IMG_PATH + file_name, cv2.IMREAD_COLOR)
    
        face_list = cascade.detectMultiScale(img, scaleFactor = 1.1, minNeighbors=1, minSize=(1, 1))
        
        for x, y, w, h in face_list:
            roi = img[y : y + h, x : x + w]
            roi[:] = mosaic(roi)
        

        cv2.imwrite('./img/face_rectangle.jpg', img)

        await ctx.send(file=discord.File("./img/face_rectangle.jpg"))
        os.remove(IMG_PATH + file_name)
        os.remove("./img/face_rectangle.jpg")

async def setup(bot: commands.Bot):
    await bot.add_cog(Image(bot))