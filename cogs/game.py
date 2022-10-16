import asyncio
import random

import akinator
import discord
from akinator.async_aki import Akinator
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import BucketType

aki = Akinator()
emojis_c = ['✅', '❌', '🤷', '👍', '👎', '⏮', '🛑']
emojis_w = ['✅', '❌']
errortxt = ('error')
errortxt = ''.join(errortxt)

def w(name, desc, picture):
    embed_win = discord.Embed(title=f"貴方が思い浮かべているのは... {name} ({desc})! 正解？",
                              colour=discord.Colour.from_rgb(255, 208, 0))
    embed_win.set_image(url=picture)
    return embed_win

class Game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Game Cog is now ready!")

    @commands.hybrid_command(name="akinator", description="アキネイターをプレイ", with_app_command=True)    
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    async def guess(self, ctx: commands.Context):
        await ctx.defer()
        desc_loss = ''
        d_loss = ''

        def check_c(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in emojis_c and reaction.message.content == q

        def check_w(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emojis_w

        try:
            q = await aki.start_game(language="jp")
                
            
            embed_question = discord.Embed(
                title=
                ':person_wearing_turban: アキネイター:person_wearing_turban: ',
                description=f"やあ、こんにちは。{ctx.author.mention} 私はアキネイターだ。貴方が思い浮かべている人物を当ててみせよう。",
                color=discord.Colour.from_rgb(255, 208, 0))
            embed_question.set_thumbnail(url="https://en.akinator.com/bundles/elokencesite/images/akinator.png?v93")
            embed_question.add_field(name="プレイ方法", value="✅: はい,  ❌: いいえ,  🤷: わからない,  👍: たぶん/部分的にそう,  👎: たぶん違う,  ⏮: 一つ前に戻る,  🛑: 終了")
            await ctx.send(embed=embed_question)

            while aki.progression <= 85:
                message = await ctx.send(q)

                for m in emojis_c:
                    await message.add_reaction(m)

                try:
                    symbol, username = await self.bot.wait_for('reaction_add',
                                                        timeout=45.0,
                                                        check=check_c)
                except asyncio.TimeoutError:
                    embed_game_ended = discord.Embed(
                        title='長時間放置されたため、ゲームを終了します。',
                        color=discord.Colour.from_rgb(255, 208, 0))
                    await ctx.send(embed=embed_game_ended)
                    return

                if str(symbol) == emojis_c[0]:
                    a = 'y'
                elif str(symbol) == emojis_c[1]:
                    a = 'n'
                elif str(symbol) == emojis_c[2]:
                    a = 'idk'
                elif str(symbol) == emojis_c[3]:
                    a = 'p'
                elif str(symbol) == emojis_c[4]:
                    a = 'pn'
                elif str(symbol) == emojis_c[5]:
                    a = 'b'
                elif str(symbol) == emojis_c[6]:
                    embed_game_end = discord.Embed(
                        title='ゲームを終了します',
                        color=discord.Colour.from_rgb(255, 208, 0))
                    await ctx.send(embed=embed_game_end)
                    return

                if a == "b":
                    try:
                        q = await aki.back()
                    except akinator.CantGoBackAnyFurther:
                        pass
                else:
                    q = await aki.answer(a)

            await aki.win()

            wm = await ctx.send(
                embed=w(aki.first_guess['name'], aki.first_guess['description'],
                        aki.first_guess['absolute_picture_path']))

            for e in emojis_w:
                await wm.add_reaction(e)

            try:
                s, u = await self.bot.wait_for('reaction_add',
                                        timeout=30.0,
                                        check=check_w)
            except asyncio.TimeoutError:
                for times in aki.guesses:
                    d_loss = d_loss + times['name'] + '\n'
                t_loss = 'この中に正解はあるかな？ :'
                embed_loss = discord.Embed(title=t_loss,
                                        description=d_loss,
                                        color=discord.Colour.from_rgb(255, 208, 0))
                await ctx.send(embed=embed_loss)
                return

            if str(s) == emojis_w[0]:
                embed_win = discord.Embed(
                    title='魔人の勝利！',description="魔人は何でもお見通しだ！", color=discord.Colour.from_rgb(255, 208, 0))
                embed_win.set_thumbnail(url="https://i.pinimg.com/originals/ae/aa/d7/aeaad720bd3c42b095c9a6788ac2df9a.png")
                await ctx.send(embed=embed_win)
            elif str(s) == emojis_w[1]:
                for times in aki.guesses:
                    desc_loss = desc_loss + times['name'] + '\n'
                title_loss = 'お見事！..この中に正解はあるかな？ :'
                embed_loss = discord.Embed(title=title_loss,
                                        description=desc_loss,
                                        color=discord.Colour.from_rgb(255, 208, 0))
                await ctx.send(embed=embed_loss)

        except Exception as e:
            await ctx.send(e)


    @commands.Cog.listener() 
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MaxConcurrencyReached):
            title_error_four = 'Someone is already playing'
            desc_error_four = 'Please wait until the person currently playing is done with their turn'
            embed_var_four = discord.Embed(title=title_error_four,
                                        description=desc_error_four,
                                        color=discord.Colour.from_rgb(255, 208, 0))
            await ctx.send(embed=embed_var_four)

    @commands.hybrid_command(name="minesweeper", description="マインスイーパーをプレイ", with_app_command=True)    
    @app_commands.describe(columns="縦のマス数", rows="横のマス数", bombs="爆弾の数")
    async def minesweeper(self, ctx:commands.Context, columns: int, rows: int, bombs: int):
        if columns is None or rows is None and bombs is None:
            if columns is not None or rows is not None or bombs is not None:
                await ctx.send(errortxt)
                return
            else:
                columns = random.randint(4,13)
                rows = random.randint(4,13)
                bombs = columns * rows - 1
                bombs = bombs / 2.5
                bombs = round(random.randint(5, round(bombs)))
        try:
            columns = int(columns)
            rows = int(rows)
            bombs = int(bombs)
        except ValueError:
            await ctx.send(errortxt)
            return
        if columns > 13 or rows > 13:
            await ctx.send('**ERROR**  縦のマス数は13が限界です....')
            return
        if columns < 1 or rows < 1 or bombs < 1:
            await ctx.send('**ERROR**  マス数が少なすぎます...')
            return
        if bombs + 1 > columns * rows:
            await ctx.send('**ERROR**  :boom:マス数より多く爆弾の数が設定されています')
            return

        grid = [[0 for num in range (columns)] for num in range(rows)]

        loop_count = 0
        while loop_count < bombs:
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)

            if grid[y][x] == 0:
                grid[y][x] = 'B'
                loop_count = loop_count + 1

            if grid[y][x] == 'B':
                pass

        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            adj_sum = 0
            for (adj_y, adj_x) in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)]:
                try:
                    if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
                        adj_sum = adj_sum + 1
                except Exception as error:
                    pass
            if grid[pos_y][pos_x] != 'B':
                grid[pos_y][pos_x] = adj_sum

            if pos_x == columns - 1:
                pos_x = 0
                pos_y = pos_y + 1
            else:
                pos_x = pos_x + 1

        string_builder = []
        for the_rows in grid:
            string_builder.append(''.join(map(str, the_rows)))
        string_builder = '\n'.join(string_builder)

        string_builder = string_builder.replace('0', '||:zero:||')
        string_builder = string_builder.replace('1', '||:one:||')
        string_builder = string_builder.replace('2', '||:two:||')
        string_builder = string_builder.replace('3', '||:three:||')
        string_builder = string_builder.replace('4', '||:four:||')
        string_builder = string_builder.replace('5', '||:five:||')
        string_builder = string_builder.replace('6', '||:six:||')
        string_builder = string_builder.replace('7', '||:seven:||')
        string_builder = string_builder.replace('8', '||:eight:||')
        final = string_builder.replace('B', '||:bomb:||')

        percentage = columns * rows
        percentage = bombs / percentage
        percentage = 100 * percentage
        percentage = round(percentage, 2)

        embed = discord.Embed(title='\U0001F4A3 マインスイーパー \U0001F4A3', color=0xC0C0C0)
        embed.add_field(name='縦マス数:', value=columns, inline=True)
        embed.add_field(name='横マス数:', value=rows, inline=True)
        embed.add_field(name='マス合計:', value=columns * rows, inline=True)
        embed.add_field(name='マインの数:', value=bombs, inline=True)
        embed.add_field(name='マインの確率:', value=f'{percentage}%', inline=True)
        embed.add_field(name='作成者:', value=ctx.author.display_name, inline=True)
        await ctx.send(content=f'\U0000FEFF\n{final}', embed=embed)

    @minesweeper.error
    async def minesweeper_error(self, ctx: commands.Context, error):
        await ctx.send(errortxt)
        return

    @commands.hybrid_command(name="rps", description="じゃんけん", with_app_command=True)    
    async def rps(self, ctx: commands.Context):
        embed = discord.Embed(title=None, description=None)
        embed.set_image(url="https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411174821.gif")
        view = RpsView()
        await ctx.send(embed=embed,view=view)

rpsready = 'https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411174821.gif'
#rpswin = 'https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411191123.gif'
rpslose = 'https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411175128.png'
rpshondawin = ['https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411191123.gif','https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411192656.png', 'https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411192619.png', 'https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411192839.png']
rpsGame = ['グー', 'チョキ', 'パー']
comp_choice = random.choice(rpsGame)

embedlose=discord.Embed(title=None, description=f"俺の手は{comp_choice}")
embedlose.set_image(url="https://cdn-ak.f.st-hatena.com/images/fotolife/k/kiji0621/20190411/20190411175128.png")

embedwin=discord.Embed(title=None, description=f"俺の手は{comp_choice}")
embedwin.set_image(url=f"{random.choice(rpshondawin)}")

class RpsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(style=discord.ButtonStyle.green, label="グー", row=1)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if comp_choice == 'グー':
            return await interaction.response.edit_message(content=f"あいこや....しょーもな....俺の手は{comp_choice}", view=None)
        elif comp_choice == 'パー':
            return await interaction.response.edit_message(embed=embedlose, view=None)
        elif comp_choice == 'チョキ':
            return await interaction.response.edit_message(embed=embedwin, view=None)
            
    @discord.ui.button(style=discord.ButtonStyle.green, label="パー", row=1)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        if comp_choice == 'グー':
            return await interaction.response.edit_message(embed=embedwin, view=None)
        elif comp_choice == 'パー':
            return await interaction.response.edit_message(content=f'あいこや....しょーもな....俺の手は{comp_choice}', view=None)
        elif comp_choice == 'チョキ':
            return await interaction.response.edit_message(embed=embedlose, view=None)
            
    @discord.ui.button(style=discord.ButtonStyle.green, label="チョキ", row=1)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        if comp_choice == 'グー':
            return await interaction.response.edit_message(embed=embedlose, view=None)
        elif comp_choice == 'パー':
            return await interaction.response.edit_message(embed=embedwin, view=None)            
        elif comp_choice == 'チョキ':
            return await interaction.response.edit_message(content=f'あいこや....しょーもな....俺の手は{comp_choice}', view=None)

async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))


    