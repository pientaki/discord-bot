import psycopg2
from discord import app_commands
from discord.ext import commands
import os
import discord

pw = os.environ["dbpw"]
host = os.environ["host"]
dsn = f"port=5432 dbname=postgres host={host} user=postgres password={pw}"
conn = psycopg2.connect(dsn)
cur = conn.cursor()

class Tag(discord.ui.Modal, title='タグ'):
    name = discord.ui.TextInput(
        label='タイトル',
        placeholder='タイトル',
    )
    
    content = discord.ui.TextInput(
        label='内容',
        style=discord.TextStyle.long,
        placeholder='タグの内容を入力して下さい',
        required=False,
        max_length=2000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        sql = "INSERT INTO tags (title, content) VALUES (%s, %s)"
        cur.execute(sql, (self.name.value, self.content.value))
        await interaction.response.send_message(f'タグ ***{self.name.value}*** が正常に作成されました', ephemeral=True)
        cur.close
        conn.close


    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('エラーが発生しました', ephemeral=True)


class DB(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("DB Cog is now ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        cur.execute("SELECT * FROM app_user WHERE userid= %s AND guild = %s", (message.author.id, message.guild.id,))
        data=cur.fetchone()

        if data is None:
            cur.execute("INSERT INTO app_user VALUES (%s, %s, %s, %s)",(message.author.id, 1, 0, message.guild.id,))
            conn.commit()
            return
        cur.execute("UPDATE app_user set xp=%s WHERE userid=%s AND guild = %s",(data[2]+1, message.author.id, message.guild.id,))
        conn.commit()
        cur.execute("SELECT * FROM app_user WHERE userid=%s AND guild = %s", (message.author.id, message.guild.id,))
        data=cur.fetchone()
        if data[2] >= data[1]*5:
            cur.execute("UPDATE app_user set level=%s,xp=%s WHERE userid=%s AND guild = %s",(data[1]+1,0,message.author.id, message.guild.id,))
            conn.commit()
            await message.channel.send(f"{message.author.mention}がレベル{data[1]+1}になりました")
        cur.close
        conn.close

    @commands.hybrid_command(name="level", description="ユーザーのレベルを表示します", with_app_command=True)
    @app_commands.rename(member="メンバー")    
    @app_commands.describe(member="メンバーを選択して下さい")
    async def level(self, ctx: commands.Context, member:discord.User=None):
        guild = ctx.guild
        if member is None:
            user=ctx.author
        else:
            user=member
        cur.execute("SELECT * FROM app_user WHERE userid=%s AND guild = %s", (user.id, guild.id,))
        data=cur.fetchone()
        if data is None:
            await ctx.send("ユーザーが登録されていません")
        e=discord.Embed(title=f"{user}のランク", description=f"Lv.{data[1]}", color=discord.Colour.gold())
        await ctx.send(embed=e)
        cur.close
        conn.close

    @app_commands.Group(description="Tag commands")
    async def tag(self, interaction: discord.Interaction):    
        await interaction.response.send_message("Tag commands")


    @tag.command(name = "create", description = "タグを作成します")
    async def tag(self, interaction: discord.Interaction):
        await interaction.response.send_message("タグを作成します..", ephemeral=True)
        await interaction.response.send_modal(Tag())

    @tag.command(name = "get", description = "タグを取得します")
    @app_commands.describe(name="タグのタイトルを入力して下さい")
    async def tag(self, interaction: discord.Interaction, name: str):
        try:
        
            cur.execute("SELECT content FROM tags WHERE title= %s ", (name,))
            data=cur.fetchone()

            await interaction.response.send_message(data[0])

            cur.close
            conn.close


        except Exception:
            await interaction.response.send_message("タグが見つかりません </tagsearch:1052607497690681406> で名前を確認してください")

        
    @tag.command(name = "search", description = "タグのタイトル一覧を表示します")
    @app_commands.describe(name="タグのタイトルを入力して下さい")
    async def tag(self, interaction: discord.Interaction):
        cur.execute("SELECT title FROM tags")
        data = cur.fetchall()
        result_1d = [row[0] for row in data]
        datafix = '\n'.join(result_1d)

        embed = discord.Embed(title="タグ一覧", description=datafix, color=discord.Colour.gold())

        await interaction.response.send_message(embed=embed)

        cur.close
        conn.close

async def setup(bot: commands.Bot):
    await bot.add_cog(DB(bot))


