import os
from itertools import cycle
import discord
from discord.ext import commands, tasks
from jishaku.features.python import PythonFeature
from data.help import MUSICEBD, CONVEBD, MODEBD, SVEBD, FUNEBD, GAMEEBD, SUBEBD

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
        await self.tree.sync()
        await self.load_extension("jishaku")
        print(f"Synced slash commands for {self.user}.")
        print("JISHAKU")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error)
    
bot = Bot()


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

    class Dropdown(discord.ui.Select):
        def __init__(self):

            options=[discord.SelectOption(label="音楽コマンド", description="音楽コマンド一覧", emoji="<a:beat:1037376715653128262>"), discord.SelectOption(label="サーバー系コマンド", description="サーバー系コマンド一覧", emoji="<:server:1037738456195006524>"), discord.SelectOption(label="管理コマンド", description="管理コマンド一覧", emoji="🎛️"),
            discord.SelectOption(label="便利系コマンド", description="便利系コマンド一覧", emoji="🔎"), discord.SelectOption(label="ゲームコマンド", description="ゲームコマンド一覧", emoji="<a:gamer:1037738473110651001>"), discord.SelectOption(label="ネタコマンド", description="ネタコマンド一覧", emoji="<a:laugh:1037738493583036416>"), discord.SelectOption(label="その他", description="その他の機能", emoji="🕶️"),
            discord.SelectOption(label="ホーム", description="ホームに戻る", emoji="🏠")]
        
            super().__init__(placeholder='コマンドのジャンルを選択して下さい', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            if self.values[0] == "音楽コマンド":
                await interaction.response.edit_message(embed=MUSICEBD)
            elif self.values[0] == "管理コマンド":
                await interaction.response.edit_message(embed=MODEBD)
            elif self.values[0] == "便利系コマンド":
                await interaction.response.edit_message(embed=CONVEBD)
            elif self.values[0] == "サーバー系コマンド":
                await interaction.response.edit_message(embed=SVEBD)
            elif self.values[0] == "ゲームコマンド":
                await interaction.response.edit_message(embed=GAMEEBD)
            elif self.values[0] == "ネタコマンド":
                await interaction.response.edit_message(embed=FUNEBD)
            elif self.values[0] == "その他":
                await interaction.response.edit_message(embed=SUBEBD)
            elif self.values[0] == "ホーム":
                await interaction.response.edit_message(embed=helpembed)
        
    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(Dropdown())

    view = DropdownView()
    await ctx.send(embed=helpembed, view=view)


'''
@bot.tree.command(name="sync", description="スラッシュコマンド登録,owner only")
async def treesync(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message("スラッシュコマンドを登録しました", ephemeral=True)
'''

bot.run(os.environ["token"])

