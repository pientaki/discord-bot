import os
import PIL.ImageFilter
import PIL.Image
import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
import qrcode
from pyzbar.pyzbar import decode


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
        pfp = PIL.Image.open(data)

        nwpfp = pfp.convert("L")

        nwpfp.save("./img/avater.jpg")

        await ctx.send(file=discord.File("./img/avater.jpg"))
        os.remove("./img/avater.jpg")

    @image.command(name="monochrome",with_app_command = True, description="白黒画像を生成します")
    @app_commands.rename(img="画像")    
    @app_commands.describe(img="対応フォーマットは png jpg です")
    async def imgmono(self, ctx: commands.Context, img: discord.Attachment):
       

        data = BytesIO(await img.read())
        pfp = PIL.Image.open(data)

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
        pfp = PIL.Image.open(data)

        pfp_list = []

        for i in range(35,0,-1):    
            pfp_r = pfp.filter(PIL.ImageFilter.GaussianBlur(i))
            pfp_list.append(pfp_r)

        pfp_list[0].save('./img/blur.gif', save_all=True, append_images=pfp_list[1:], optimize=True, duration=200, loop=0)  
    
        await ctx.send(file=discord.File("./img/blur.gif"))
        os.remove("./img/blur.gif")

    @commands.hybrid_group()
    async def qr(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Qrcode commands")

    @qr.command(name="create",with_app_command = True, description="QRコードを生成します")
    @app_commands.rename(data="データ")    
    @app_commands.describe(data="データを入力して下さい")
    async def qr(self, ctx: commands.Context, data: str):
        await ctx.defer()

        qr_img = qrcode.make(data)
        qr_img.save("./img/code.png")

        await ctx.send(file=discord.File("./img/code.png"))
        os.remove("./img/code.png")

    @qr.command(name="read",with_app_command = True, description="QRコードを読み取ります")
    @app_commands.rename(img="画像")    
    @app_commands.describe(img="Qrコードを添付して下さい")
    async def qrread(self, ctx: commands.Context, img: discord.Attachment):
        await ctx.defer()

        data = BytesIO(await img.read())
        pfp = decode(PIL.Image.open(data))

        await ctx.send(pfp[0].data.decode("utf-8"))

    


async def setup(bot: commands.Bot):
    await bot.add_cog(Image(bot))