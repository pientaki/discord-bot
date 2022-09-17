import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta 
import asyncio

class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Server Cog is now ready!")

    @commands.hybrid_command(name="server", description="サーバー情報を表示", with_app_command=True)
    async def server_info(self, ctx: commands.Context):
        owner=str(ctx.guild.owner)
        guild_id = str(ctx.guild.id)
        memberCount = str(ctx.guild.member_count)
        icon = str(ctx.guild.icon)
        desc=ctx.guild.description
        no_voice_channels = len(ctx.guild.voice_channels)
        no_text_channels = len(ctx.guild.text_channels)
        role_count = len(ctx.guild.roles)
        list_of_bots = [bot.mention for bot in ctx.guild.members if bot.bot]
        vlev = str(ctx.guild.verification_level)
        emoji_string = ""
        for e in ctx.guild.emojis:
            if e.is_usable():
                emoji_string += str(e)
    
        embed = discord.Embed(
            title=ctx.guild.name + " サーバー情報",
            description=desc,
            color=ctx.author.color
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="🔹ID", value=guild_id, inline=True)
        embed.add_field(name="🔹認証レベル", value=vlev, inline=True)
        embed.add_field(name="🔹オーナー", value=owner, inline=False)
        embed.add_field(name="🔹メンバー数", value=memberCount, inline=True)
        embed.add_field(name="🔹Bot", value=(', '.join(list_of_bots)), inline=True)
        embed.add_field(name="🔹ボイスチャンネル数", value=no_voice_channels, inline=False)
        embed.add_field(name="🔹テキストチャンネル数", value=no_text_channels, inline=False)
        embed.add_field(name="🔹最高ロール", value=ctx.guild.roles[-2], inline=True)
        embed.add_field(name="🔹ロール数", value=str(role_count), inline=True)
        embed.add_field(name="🔹作成日時", value=discord.utils.format_dt(ctx.guild.created_at))

        embed2 = discord.Embed(
            title="サーバー絵文字一覧",
            description=emoji_string,
            color=ctx.author.color
        )

        embeds = [embed,embed2]

        await ctx.send(embeds=embeds)

    @commands.hybrid_command(name="user-info", description="ユーザー情報を表示", with_app_command=True)    
    @app_commands.describe(member="メンバーを選択して下さい")
    async def user_info(self, ctx: commands.Context, member: discord.Member):
        embed = discord.Embed(title=str(member), color=discord.Color.blue())
        embed.add_field(name="🔹作成日時", value=discord.utils.format_dt(member.created_at), inline=False)
        embed.add_field(name="🔹ID", value=member.id, inline=False)
        embed.add_field(name="🔹サーバー参加日時", value=discord.utils.format_dt(member.joined_at), inline=False)
        embed.set_thumbnail(url=member.avatar)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kick", description="メンバーをキックします", with_app_command=True)
    @commands.has_permissions(kick_members=True)    
    @app_commands.describe(member="メンバーを選択して下さい", reason = "キックする理由を入力して下さい")
    async def kick(self, ctx: commands.Context, member: discord.Member, reason):
        try:
            await member.kick(reason=reason)
            embed=discord.Embed(title="KICK", color=discord.Color.from_rgb(255, 0, 0))
            embed.add_field(name="メンバー", value=f"{member.mention}", inline=False)
            embed.add_field(name="理由", value=f"{reason}", inline=False)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("あなたにはキック権限がありません")

    @commands.hybrid_command(name="ban", description="メンバーをBanします", with_app_command=True)
    @commands.has_permissions(ban_members=True)    
    @app_commands.describe(member="メンバーを選択して下さい", reason = "Banする理由を入力して下さい")
    async def ban(self, ctx: commands.Context, member: discord.Member, reason):
        try:
            await member.ban(reason=reason)
            embed=discord.Embed(title="BAN", color=discord.Color.from_rgb(255, 0, 0))
            embed.add_field(name="メンバー", value=f"{member.mention}", inline=False)
            embed.add_field(name="理由", value=f"{reason}", inline=False)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("あなたにはBan権限がありません")

    @commands.hybrid_command(name="timeout", description="メンバーをタイムアウトします", with_app_command=True)    
    @app_commands.describe(member="メンバーを選択して下さい", reason = "理由を入力して下さい",days="タイムアウトする日数を入力してください(0-27)", hours="タイムアウトする時間を入力してください(0-24)", minutes="タイムアウトする分を入力してください(0-60)",seconds="タイムアウトする秒数を入力してください(0-60)")
    async def timeout(self, ctx: commands.Context, member: discord.Member, reason: str,  days: app_commands.Range[int, 0, 27], hours: app_commands.Range[int, 0, 24] , minutes: app_commands.Range[int, 0, 60], seconds:app_commands.Range[int, 0, 60]):
        embed=discord.Embed(title="タイムアウト", color=discord.Color.from_rgb(255, 0, 0))
        embed.add_field(name="対象者", value=f"{member.mention}", inline=False)
        embed.add_field(name="実行者", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="期間", value=f"{days}日{hours}時間{minutes}分{seconds}秒", inline=False)
        embed.add_field(name="理由", value=f"{reason}", inline=False)
        duration = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
        if duration >= timedelta(days = 28):
            await ctx.send("28日以上は設定できません", ephemeral = True) 
            return
        else:
            await member.timeout(duration, reason=reason)
            await ctx.send(embed=embed)
        await member.send(f"あなたは `{ctx.guild}` でタイムアウトされました\n"
        f"理由: `{reason}`\n" f"期間: `{days}日{hours}時間{minutes}分{seconds}秒`\n"
        f"詳しくは実行者{ctx.author.mention}、又は{ctx.guild.owner.mention}までお問い合わせ下さい")

    @commands.hybrid_command(name="removetimeout", description="メンバーのタイムアウトを解除します", with_app_command=True)   
    @app_commands.describe(member="メンバーを選択して下さい")
    async def remove_timeout(self, ctx: commands.Context, member: discord.Member, reason=None):
        await member.timeout(None, reason=reason)
        embed=discord.Embed(title="タイムアウト解除", color=discord.Color.blue())
        embed.add_field(name="対象者", value=f"{member.mention}", inline=False)
        embed.add_field(name="実行者", value=f"{ctx.author.mention}", inline=False)
        await ctx.send(embed=embed)
        await member.send(f"あなたの `{ctx.guild}` でのタイムアウトは解除されました\n")

    @commands.hybrid_command(name="mute", description="メンバーをミュートします", with_app_command=True)    
    @app_commands.describe(member="メンバーを選択して下さい", reason = "ミュートする理由を入力して下さい", role="ロールがある場合は取り除くロール名を入れて下さい")
    async def mute(self, ctx: commands.Context, member: discord.Member, reason: str, role: discord.Role = None):
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name = "ミュート中")
        if not mutedRole:
            await ctx.send("ロールを作成中")
            mutedRole = await guild.create_role(name = "ミュート中")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
        await member.add_roles(mutedRole, reason=reason)
        embed = discord.Embed(title="ミュート",color=discord.Color.from_rgb(255, 0, 0))
        embed.description =(f"{member.mention} は {ctx.guild} でミュートされました\n"
        f"理由: {reason}")
        await ctx.send(embed=embed)
        await member.send(f"あなたは `{ctx.guild}` でミュートされました\n"
        f"理由: `{reason}`"
        f"詳しくは実行者{ctx.author.mention}、又は{ctx.guild.owner.mention}までお問い合わせ下さい")
        if role == None:
            return
        else:
            await member.remove_roles(role)

    @commands.hybrid_command(name="removemute", description="メンバーをミュートを解除します", with_app_command=True)    
    @app_commands.describe(member="メンバーを選択して下さい")
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        mutedRole = discord.utils.get(ctx.guild.roles, name="ミュート中")
        await member.remove_roles(mutedRole)
        embed = discord.Embed(title="ミュート解除",color=discord.Color.blurple())
        embed.description = (f"{member.mention} のミュートが解除されました")
        await ctx.send(embed=embed)
        await member.send(f"あなたの `{ctx.guild.name}` でのミュートは解除されました")

    @commands.hybrid_command(name="clear", description="送信したメッセージを消去します", with_app_command=True)    
    @app_commands.describe(amount="削除したい件数を入力して下さい")
    async def clear(self, ctx: commands.Context, amount: int):
        await ctx.send(f"メッセージが{amount}件分削除されます")
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=amount)
        

    @commands.hybrid_command(name="ping", description="botのping値を測定します", with_app_command=True)    
    async def ping(self, ctx: commands.Context):
        raw_ping = self.bot.latency
        ping = round(raw_ping * 1000)
        embed = discord.Embed(title="🏓Ping",color=discord.Color.blurple())
        embed.description = (f"BotのPing値は**{ping}**msです")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Server(bot))
