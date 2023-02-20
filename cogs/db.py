import asyncpg
from discord import app_commands
from discord.app_commands import Group
from discord.ext import commands
import os
import discord
import datetime

pw = os.environ["dbpw"]
host = os.environ["host"]
dsn = f"postgresql://postgres:{pw}@{host}:5432/postgres"


class Tag(discord.ui.Modal, title='タグ'):
    name = discord.ui.TextInput(
        label='タイトル',
        placeholder='タイトル',
    )
    
    content = discord.ui.TextInput(
        label='内容(2000字以内)',
        style=discord.TextStyle.long,
        placeholder='タグの内容を入力して下さい',
        required=False,
        max_length=2000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        conn = await asyncpg.connect(dsn)
        await conn.execute("INSERT INTO tags (title, content) VALUES ($1, $2)", self.name.value, self.content.value)
        await interaction.response.send_message(f'タグ ***{self.name.value}*** が正常に作成されました', ephemeral=True)
        await conn.close()


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('エラーが発生しました', ephemeral=True)


class dab(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    tg = Group(name='tag', description='tag-commands')


    @commands.Cog.listener()
    async def on_ready(self):
        print("DB Cog is now ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        conn = await asyncpg.connect(dsn)
        if message.author.bot:
            return

        data= await conn.fetchrow("SELECT * FROM app_user WHERE userid= $1 AND guild = $2", message.author.id, message.guild.id)

        if data is None:
            await conn.execute("INSERT INTO app_user VALUES ($1, $2, $3, $4)",message.author.id, 1, 0, message.guild.id)
            return
        await conn.execute("UPDATE app_user set xp=$1 WHERE userid=$2 AND guild = $3",data[2]+1, message.author.id, message.guild.id)

        if data[2] >= data[1]*5:
            await conn.execute("UPDATE app_user set level=$1,xp=$2 WHERE userid=$3 AND guild = $4",data[1]+1,0,message.author.id, message.guild.id)
            await message.channel.send(f"{message.author.mention}がレベル{data[1]+1}になりました")
        await conn.close()

    @commands.hybrid_command(name="level", description="ユーザーのレベルを表示します", with_app_command=True)
    @app_commands.rename(member="メンバー")    
    @app_commands.describe(member="メンバーを選択して下さい")
    async def level(self, ctx: commands.Context, member:discord.User=None):
        conn = await asyncpg.connect(dsn)
        guild = ctx.guild
        if member is None:
            user=ctx.author
        else:
            user=member
        data = await conn.fetchrow("SELECT * FROM app_user WHERE userid= $1 AND guild = $2", user.id, guild.id)
        if data is None:
            await ctx.send("ユーザーが登録されていません")
        e=discord.Embed(title=f"{user}のランク", description=f"Lv.{data[1]}", color=discord.Colour.gold())
        await ctx.send(embed=e)
        await conn.close()


    @tg.command(name = "create", description = "タグを作成します")
    async def tag(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Tag())

    @tg.command(name = "get", description = "タグを取得します")
    @app_commands.describe(name="タグのタイトルを入力して下さい")
    async def tag(self, interaction: discord.Interaction, name: str):
        conn = await asyncpg.connect(dsn)
        try:        
            data = await conn.fetchrow("SELECT content FROM tags WHERE title= $1 ", name)
            await interaction.response.send_message(data[0])

            await conn.close()


        except Exception:
            await interaction.response.send_message("タグが見つかりません </tag search:1052607497690681404> で名前を確認してください")

        
    @tg.command(name = "search", description = "タグのタイトル一覧を表示します")
    async def tag(self, interaction: discord.Interaction):
        conn = await asyncpg.connect(dsn)
        data = await conn.fetch("SELECT title FROM tags")
        result_1d = [row[0] for row in data]
        datafix = '\n'.join(result_1d)

        embed = discord.Embed(title="タグ一覧", description=datafix, color=discord.Colour.gold())

        await interaction.response.send_message(embed=embed)
        await conn.close()

    @commands.hybrid_command(name="deleted-message", description="削除されたメッセージ一覧を表示します", with_app_command=True)
    async def snipe(self, ctx: commands.Context, member: discord.Member):
        guild = ctx.guild
        conn = await asyncpg.connect(dsn)
        try:
            data = await conn.fetch("SELECT content FROM snipe WHERE userid = $1 AND guild = $2", member.id, guild.id)
            data2 = await conn.fetch("SELECT time FROM snipe WHERE userid = $1 AND guild = $2", member.id, guild.id)
            result_1d = [row[0] for row in data]
            result2_1d = [row[0] for row in data2]
            embed = discord.Embed(title="削除済メッセージ", color=discord.Color.red())
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar)

            for (content, time) in zip(result_1d, result2_1d):
                embed.add_field(name=discord.utils.format_dt(time), value=content)
            
            await ctx.send(embed = embed)

            await conn.close()
        
                
        except Exception as e:
            await ctx.send(e)
            return
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        conn = await asyncpg.connect(dsn)
        time = message.created_at + datetime.timedelta(hours= 9) 
        
        await conn.execute("INSERT INTO snipe (content, userid, guild, time) VALUES ($1, $2, $3, $4)", message.content, message.author.id, message.guild.id,  time)
        await conn.close()



    

async def setup(bot: commands.Bot):
    await bot.add_cog(dab(bot))


