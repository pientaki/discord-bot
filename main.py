import discord
from discord.ext import commands, tasks
from discord import app_commands
from itertools import cycle
import os

status=cycle(["/cmdでコマンド一覧","Apex","Among us","Rogue Company"])
prefixes = ["!","?"]

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix = prefixes, intents = intents, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error)
    
bot = Bot()

musicembed = discord.Embed(title="**:headphones: 音楽コマンド**",color=discord.Color.blurple())
musicembed.description=(f"**/play ＜タイトル＞ : **音楽を検索して再生\n"
f"**/playstream ＜url＞ : **urlから音楽を再生\n"
f"**/stop : **音声を停止\n"
f"**/skip : **スキップ\n"    
f"**/resume : **再生\n"
f"**/pause : **一時停止\n"
f"**/queue : **キュー覧を表示\n"
f"**/pause : **一時停止\n"
f"**/volume ＜音量＞ : **音量を変更\n"
f"**/disconnect : **ボイスチャンネルから切断\n"
f"**/bassboost : **低音をブースト\n"
f"**/boostremove : **ブースト解除\n")

convembed = discord.Embed(title="**:mag_right:  便利？コマンド**",color=discord.Color.blurple())
convembed.description=(f"**/trans ＜翻訳したい言語＞ ＜内容＞ : **翻訳機能\n"
f"**/language : **翻訳言語一覧\n"
f"**/search ＜検索ワード＞ : **ネットで検索\n"
f"**/imagesearch : **ネット上の画像を検索\n"
f"**/calculator : **計算機\n")

serverembed = discord.Embed(title="**:computer: サーバーコマンド**",color=discord.Color.blurple())
serverembed.description=(f"**/kick ＜メンバー＞ : **メンバーをキック\n"
f"**/ban ＜メンバー＞ : **メンバーをban\n"
f"**/clear ＜消去数＞ : **メッセージを削除\n"
f"**/mute ＜メンバー＞ : **メンバーをミュート\n"
f"**/unmute ＜メンバー＞ : **ミュート解除\n"
f"**/user-info ＜メンバー＞ : **メンバー情報\n"
f"**/timeout ＜メンバー＞ : **メンバーをタイムアウト\n"
f"**/removetimeout ＜メンバー＞ : **タイムアウト解除\n"
f"**/activity ＜アクティビティー＞ : **botの～をプレイ中の部分を変更\n"
f"**/lederboard : **リーダーボードを表示\n"
f"**/stats ＜メンバー＞ : **ステータスを表示\n"
f"**/ping : **botのpingを表示\n")

gameembed = discord.Embed(title="**:video_game: ゲームコマンド**",color=discord.Color.blurple())
gameembed.description=(f"**/akinator : **アキネイターをプレイ\n"
f"**/minesweeper : **マインスイーパーをプレイ\n")

funembed = discord.Embed(title="**💩 その他コマンド**",color=discord.Color.blurple())
funembed.description=(f"**/meme : **ミームを投稿\n"
f"**/hack : **ハッキングツール？\n"
f"**/kodane : **褒美だ.......\n"
f"**かすが : **春日..\n"
f"**メンション ＜テキスト＞  : **AIとおしゃべり\n"
f"**リアクション ＜:flag_us:＞  : **メッセージを英語に翻訳\n"
f"**リアクション ＜:flag_in:＞  : **メッセージをヒンディー語に翻訳\n")
       
class Dropdown(discord.ui.Select):
    def __init__(self):

        options=[discord.SelectOption(label="音楽コマンド", description="音楽聞く時のコマンド一覧", emoji="🎶"), discord.SelectOption(label="サーバーコマンド", description="サーバーコマンド一覧", emoji="💻"),
        discord.SelectOption(label="便利コマンド", description="そんな便利でもないコマンド一覧", emoji="🔎"), discord.SelectOption(label="ゲームコマンド", description="ゲームコマンド一覧", emoji="🎮"), discord.SelectOption(label="その他コマンド", description="しょーもないコマンド一覧", emoji="💩")]
    
        super().__init__(placeholder='コマンドのジャンルを選択して下さい', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "音楽コマンド":
            await interaction.response.edit_message(embed=musicembed)
        elif self.values[0] == "サーバーコマンド":
            await interaction.response.edit_message(embed=serverembed)
        elif self.values[0] == "便利コマンド":
            await interaction.response.edit_message(embed=convembed)
        elif self.values[0] == "ゲームコマンド":
            await interaction.response.edit_message(embed=gameembed)
        elif self.values[0] == "その他コマンド":
            await interaction.response.edit_message(embed=funembed)
       
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
    helpembed = discord.Embed(title="Sorrows Official Bot",color=discord.Color.blurple())
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
    helpembed = discord.Embed(title="Sorrows Official Bot",color=discord.Color.blurple())
    helpembed.set_thumbnail(url=bot.user.avatar.url)
    helpembed.add_field(name="導入サーバー数", value=len(bot.guilds))
    helpembed.add_field(name="メンバー数", value=len(bot.users))
    helpembed.add_field(name="Ping", value=f"{bot.latency*1000:.2f}ms")
    view = DropdownView()
    await interaction.response.send_message(embed=helpembed, view=view)

bot.run(os.environ["token"])

