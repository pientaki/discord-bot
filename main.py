import datetime
import os
from itertools import cycle
import psycopg2
import discord
from discord import app_commands
from discord.ext import commands, tasks
from jishaku.features.python import PythonFeature

status=cycle(["/help","Apex","Among us","Rogue Company"])
prefixes = ["!","?"]

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix = prefixes, intents = intents, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.load_extension("jishaku")
        print(f"Synced slash commands for {self.user}.")
        print("JISHAKU")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error)
    
bot = Bot()

musicembed = discord.Embed(title="**<a:beat:1037376715653128262> 音楽コマンド**",color=discord.Color.blurple())
musicembed.add_field(name="play ＜タイトル又はURL＞", value="音楽をタイトル名又はURLから検索して再生します。YouTube、Twitch、Spotify、Vimeo、SoundCloudに対応しています", inline=False)
musicembed.add_field(name="stop", value="キューを全て削除して音楽を停止します", inline=False)
musicembed.add_field(name="pause", value="音楽を一時停止します", inline=False)
musicembed.add_field(name="resume", value="一時停止した音楽を再生します", inline=False)
musicembed.add_field(name="skip", value="音楽をスキップします", inline=False)
musicembed.add_field(name="queue", value="キュー覧を表示します", inline=False)
musicembed.add_field(name="volume ＜音量＞", value="音量を変更します", inline=False)
musicembed.add_field(name="disconnect", value="ボイスチャンネルから退出します", inline=False)
musicembed.add_field(name="bassboost", value="低音をブーストします", inline=False)
musicembed.add_field(name="removeboost", value="ブーストを解除します", inline=False)

convembed = discord.Embed(title="**:mag_right:  便利系コマンド**",color=discord.Color.blurple())
convembed.add_field(name="translate ＜翻訳言語＞ ＜テキスト＞", value="翻訳します", inline=False)
convembed.add_field(name="translate-language", value="翻訳言語一覧を表示します", inline=False)
convembed.add_field(name="googlesearch ＜検索ワード＞", value="Googleで検索します(上位5件分)", inline=False)
convembed.add_field(name="search ＜検索ワード＞", value="インターネットの検索結果のリンクを生成します", inline=False)
convembed.add_field(name="imagesearch ＜検索ワード＞", value="画像を検索します", inline=False)
convembed.add_field(name="wiki ＜検索ワード＞", value="Wikipediaで検索します", inline=False)
convembed.add_field(name="weather ＜地名＞", value="天気を検索します", inline=False)
convembed.add_field(name="calculator", value="計算機を表示します", inline=False)

modembed = discord.Embed(title="**🎛️  管理コマンド**",color=discord.Color.blurple())
modembed.add_field(name="kick ＜メンバー＞ ＜理由＞", value="メンバーをキックします", inline=False)
modembed.add_field(name="ban ＜メンバー＞ ＜理由＞", value="メンバーをbanします", inline=False)
modembed.add_field(name="mute ＜メンバー＞ ＜理由＞", value="メンバーをミュートします", inline=False)
modembed.add_field(name="removemute ＜メンバー＞ ＜理由＞", value="メンバーのミュートを解除します", inline=False)
modembed.add_field(name="timeout ＜メンバー＞ ＜理由＞ ＜日数＞ ＜時間＞ ＜分＞ ＜秒＞", value="メンバーをタイムアウトします", inline=False)
modembed.add_field(name="removetimeout ＜メンバー＞", value="メンバーのタイムアウトを解除します", inline=False)
modembed.add_field(name="clear ＜削除件数＞", value="送信したメッセージを消去します", inline=False)

servembed = discord.Embed(title="**<:server:1037738456195006524>  サーバー系コマンド**",color=discord.Color.blurple())
servembed.add_field(name="server", value="サーバー情報を表示します", inline=False)
servembed.add_field(name="user-info", value="ユーザー情報を表示します", inline=False)
servembed.add_field(name="ping", value="botのping値を測定します", inline=False)
servembed.add_field(name="snipe", value="最新の削除されたメッセージを復元します", inline=False)
servembed.add_field(name="channel", value="チャンネルを作成します", inline=False)
servembed.add_field(name="embed", value="埋め込みメッセージを作成します", inline=False)
servembed.add_field(name="global", value="グローバルチャット用のチャンネルを作成します(グローバルチャットとは、異なるサーバー同士での会話を可能にする機能のことです)", inline=False)
servembed.add_field(name="close", value="作成したチャンネルを削除します", inline=False)

gameembed = discord.Embed(title="**<a:gamer:1037738473110651001> ゲームコマンド**",color=discord.Color.blurple())
gameembed.add_field(name="akinator", value="アキネイターをプレイ", inline=False)
gameembed.add_field(name="minesweeper", value="マインスイーパーをプレイ", inline=False)
gameembed.add_field(name="rps", value="じゃんけんします", inline=False)
gameembed.add_field(name="aidrow", value="AIがお絵描きします", inline=False)

funembed = discord.Embed(title="**<a:laugh:1037738493583036416> ネタコマンド**",color=discord.Color.blurple())
funembed.add_field(name="meme", value="ミームを表示します", inline=False)
funembed.add_field(name="gif", value="gifを送信します", inline=False)
funembed.add_field(name="kodane", value="フリッツ王から褒美をもらえます", inline=False)
funembed.add_field(name="markov", value="マルコフ連鎖で文章を生成します", inline=False)

subembed = discord.Embed(title="**🕶️ その他**",color=discord.Color.blurple())
subembed.add_field(name="メンション ＜テキスト＞", value="ソロウ君とおしゃべりできます", inline=False)
subembed.add_field(name="リアクション ＜:flag_us:＞", value="メッセージを英語に翻訳します", inline=False)
subembed.add_field(name="リアクション ＜:flag_in:＞", value="メッセージをヒンディー語に翻訳します", inline=False)

       
class Dropdown(discord.ui.Select):
    def __init__(self):

        options=[discord.SelectOption(label="音楽コマンド", description="音楽コマンド一覧", emoji="<a:beat:1037376715653128262>"), discord.SelectOption(label="サーバー系コマンド", description="サーバー系コマンド一覧", emoji="<:server:1037738456195006524>"), discord.SelectOption(label="管理コマンド", description="管理コマンド一覧", emoji="🎛️"),
        discord.SelectOption(label="便利系コマンド", description="便利系コマンド一覧", emoji="🔎"), discord.SelectOption(label="ゲームコマンド", description="ゲームコマンド一覧", emoji="<a:gamer:1037738473110651001>"), discord.SelectOption(label="ネタコマンド", description="ネタコマンド一覧", emoji="<a:laugh:1037738493583036416>"), discord.SelectOption(label="その他", description="その他の機能", emoji="🕶️")]
    
        super().__init__(placeholder='コマンドのジャンルを選択して下さい', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "音楽コマンド":
            await interaction.response.edit_message(embed=musicembed)
        elif self.values[0] == "管理コマンド":
            await interaction.response.edit_message(embed=modembed)
        elif self.values[0] == "便利系コマンド":
            await interaction.response.edit_message(embed=convembed)
        elif self.values[0] == "サーバー系コマンド":
            await interaction.response.edit_message(embed=servembed)
        elif self.values[0] == "ゲームコマンド":
            await interaction.response.edit_message(embed=gameembed)
        elif self.values[0] == "ネタコマンド":
            await interaction.response.edit_message(embed=funembed)
        elif self.values[0] == "その他":
            await interaction.response.edit_message(embed=subembed)
       
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=next(status)))

@bot.event
async def on_ready():
    change_status.start()

@bot.hybrid_command(name = "help", with_app_command = True, description = "コマンド一覧を表示")
async def help_select(ctx: commands.Context):
    helpembed = discord.Embed(title="<:sorrows:845835709066641439>  Sorrows Official Bot",color=discord.Color.blurple(), url="https://github.com/pientaki/discord-bot")
    helpembed.set_thumbnail(url=bot.user.avatar.url)
    helpembed.add_field(name="導入サーバー数", value=len(bot.guilds))
    helpembed.add_field(name="メンバー数", value=len(bot.users))
    helpembed.add_field(name="Ping", value=f"{bot.latency*1000:.2f}ms")

    view = DropdownView()
    await ctx.send(embed=helpembed, view=view)

bot.sniped_messages = {}

@bot.event
async def on_message_delete(message):
    bot.sniped_messages[message.guild.id] = (message.content, message.author, message.channel.name, message.created_at)

@bot.hybrid_command(name = "snipe", with_app_command = True, description = "最新の削除されたメッセージを復元")
async def snipe(ctx: commands.Context):
    try:
        contents, author, channel_name, time = bot.sniped_messages[ctx.guild.id]        
    except:
        await ctx.send("削除されたメッセージが見つかりません")
        return
    embed = discord.Embed(description=contents, color=discord.Color.purple(), timestamp=time)
    embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=author.avatar)
    embed.set_footer(text=f"#{channel_name}")
    await ctx.send(embed=embed)

@bot.tree.context_menu(name="コマンド一覧")
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    helpembed = discord.Embed(title="Sorrows Official Bot",color=discord.Color.blurple(), url="https://github.com/pientaki/discord-bot")
    helpembed.set_thumbnail(url=bot.user.avatar.url)
    helpembed.add_field(name="導入サーバー数", value=len(bot.guilds))
    helpembed.add_field(name="メンバー数", value=len(bot.users))
    helpembed.add_field(name="Ping", value=f"{bot.latency*1000:.2f}ms")
    view = DropdownView()
    await interaction.response.send_message(embed=helpembed, view=view)

pw = os.environ["dbpw"]
host = os.environ["host"]
dsn = f"port=5432 dbname=postgres host={host} user=postgres password={pw}"
conn = psycopg2.connect(dsn)
cur = conn.cursor()  

@bot.event
async def on_message(message):
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



@bot.hybrid_command(name = "level", with_app_command = True, description = "ユーザーのレベルを表示します")
@app_commands.rename(target="メンバー")    
async def level(ctx: commands.Context, target:discord.User=None):
    guild = ctx.guild
    if target is None:
        user=ctx.author
    else:
        user=target
    cur.execute("SELECT * FROM app_user WHERE userid=%s AND guild = %s", (user.id, guild.id,))
    data=cur.fetchone()
    if data is None:
        await ctx.send("ユーザーが登録されていません")
    e=discord.Embed(title=f"{user}のランク", description=f"Lv.{data[1]}", color=discord.Colour.gold())
    await ctx.send(embed=e)
    cur.close
    conn.close

@bot.tree.command(name="sync", description="スラッシュコマンド登録,owner only")
async def treesync(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message("スラッシュコマンドを登録しました", ephemeral=True)

bot.run(os.environ["token"])

