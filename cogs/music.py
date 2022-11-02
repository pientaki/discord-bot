import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from wavelink.ext import spotify


class Buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⏯️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button): 
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("botがボイスチャンネルに接続していません", ephemeral=True)
        
        if player.is_paused():
            await player.resume()
            mbed1 = discord.Embed(title="再生中", color=discord.Color.from_rgb(255, 255, 255))
            return await interaction.response.send_message(embed=mbed1, ephemeral=True)
        elif player.is_playing():
            await player.pause()
            mbed = discord.Embed(title="一時停止", color=discord.Color.from_rgb(255, 255, 255))
            return await interaction.response.send_message(embed=mbed, ephemeral=True)
        else:
            return await interaction.response.send_message("現在音楽は流れていません", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⏹️", row=0)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("botがボイスチャンネルに接続していません", ephemeral=True)
        
        if player.is_playing:
            player.queue.clear()
            await player.stop()
            mbed = discord.Embed(title="停止", color=discord.Color.from_rgb(255, 255, 255))
            return await interaction.response.send_message(embed=mbed, ephemeral=True)
        else:
            return await interaction.response.send_message("現在音楽は流れていません", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="⏭️", row=0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("botがボイスチャンネルに接続していません", ephemeral=True)
        
        if player.is_playing and not player.queue.is_empty:
            await player.stop()
            mbed = discord.Embed(title="スキップ", color=discord.Color.from_rgb(255, 255, 255))
            return await interaction.response.send_message(embed=mbed, ephemeral=True)
        elif player.queue.is_empty:
            return await interaction.response.send_message("キューに曲はありません")
        else:
            return await interaction.response.send_message("現在音楽は流れていません", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.red, emoji="🔚", row=0)
    async def dc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("botがボイスチャンネルに接続していません", ephemeral=True)
    
        await player.disconnect()
        mbed = discord.Embed(title="ボイスチャンネルから退出", color=discord.Color.from_rgb(255, 255, 255))
        await interaction.response.send_message(embed=mbed)

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        bot.loop.create_task(self.create_nodes())
    
    async def create_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="lavalink-replit-2.tomatotomato3.repl.co", port="443", https=True ,password="sorrows",region="asia", spotify_client=spotify.SpotifyClient(client_id="d52f6a05b7ac4ea1b953eadbd2b6ba45", client_secret="e43ff5d74bcd4eb28e55e5976b7b282e"))

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog is now ready!")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node <{node.identifier}> is now Ready!")

    @commands.hybrid_group()
    async def music(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Music commands")


    @music.command(name="play",with_app_command = True, description="YouTubeの音楽を再生")
    @app_commands.describe(search="検索ワードかURL(spotify or youtube)")    
    async def play(self, ctx: commands.Context, *, search:str):
        await ctx.defer()

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            embed=discord.Embed(title=f"ボイスチャンネル {ctx.author.voice.channel.name} に接続", color=discord.Color.from_rgb(255, 255, 255))
            await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
            vc.chanctx = ctx.channel

        if 'https://open.spotify.com' in str(search):

            if vc.queue.is_empty and not vc.is_playing():

                track = await spotify.SpotifyTrack.search(query=search, return_first=True)

                await vc.play(track)

                mbed = discord.Embed(title="<:spotify:1037380941506682920>再生中", color=discord.Color.from_rgb(255, 255, 255))
                mbed.add_field(name="🎶タイトル", value=track.title)
                mbed.add_field(name="🎶再生時間", value=round(track.duration / 60, 2))
                mbed.add_field(name="🎶ボリューム", value=vc.volume)
                mbed.add_field(name="🎶著作者", value=track.author) 
                mbed.set_image(url="https://storage.googleapis.com/spotifynewsroom-jp.appspot.com/1/2020/12/Spotify_Logo_CMYK_Green.png")

                view = Buttons()
                await ctx.send(embed=mbed, view=view)

            else:
                track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                await vc.queue.put_wait(track)
                await ctx.send(f'🎶`{track}` をキューに追加しました')

        elif 'https://www.youtube.com/' in str(search):

            if vc.queue.is_empty and not vc.is_playing():

                track1 = await vc.node.get_tracks(query=search, cls=wavelink.Track)

                await vc.play(track1[0])
                mbed = discord.Embed(title="<:youtube:1037380132056342529>再生中", color=discord.Color.from_rgb(255, 255, 255))
                mbed.add_field(name="🎶url", value=search)
                mbed.add_field(name="🎶タイトル", value=track1)
                mbed.add_field(name="🎶ボリューム", value=vc.volume) 
                mbed.set_image(url="https://wavelink.readthedocs.io/en/1.0/_static/logo.png")

                view = Buttons()

                await ctx.send(embed=mbed, view=view)


            else:
                track1 = await vc.node.get_tracks(query=search, cls=wavelink.Track)
                await vc.queue.put_wait(track1[0])
                await ctx.send(f'🎶`{track1}` をキューに追加しました')

        else:

            if vc.queue.is_empty and not vc.is_playing(): 

                track2 = await wavelink.YouTubeTrack.search(query=search, return_first=True)

                await vc.play(track2)

                mbed = discord.Embed(title="<:youtube:1037380132056342529>再生中", color=discord.Color.from_rgb(255, 255, 255))
                mbed.add_field(name="🎶タイトル", value=track2.title)
                mbed.add_field(name="🎶再生時間", value=round(track2.duration / 60, 2))
                mbed.add_field(name="🎶ボリューム", value=vc.volume)
                mbed.add_field(name="🎶チャンネル", value=track2.author) 
                mbed.set_image(url=track2.thumb)

                view = Buttons()
                await ctx.send(embed=mbed, view=view)

            else:

                track2 = await wavelink.YouTubeTrack.search(query=search, return_first=True)
                await vc.queue.put_wait(track2)
                await ctx.send(f'🎶`{track2}` をキューに追加しました')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track , reason):

        if not player.queue.is_empty:
            ctx = player.chanctx
            new_song = player.queue.get()
            await player.play(new_song)

            view = Buttons()

            if hasattr(new_song, 'thumb'):
                mbed = discord.Embed(title="再生中", color=discord.Color.from_rgb(255, 255, 255))
                mbed.add_field(name="タイトル", value=new_song.title)
                mbed.add_field(name="再生時間", value=round(new_song.duration / 60, 2))
                mbed.add_field(name="ボリューム", value=player.volume)
                mbed.add_field(name="チャンネル", value=new_song.author) 
                mbed.set_image(url=new_song.thumb) 
                await ctx.send(embed=mbed, view=view)

            else:
                mbed = discord.Embed(title="再生中", color=discord.Color.from_rgb(255, 255, 255))
                mbed.add_field(name="タイトル", value=new_song.title)
                mbed.add_field(name="再生時間", value=round(new_song.duration / 60, 2))
                mbed.add_field(name="ボリューム", value=player.volume)
                mbed.add_field(name="チャンネル", value=new_song.author) 
                mbed.set_image(url="https://wavelink.readthedocs.io/en/1.0/_static/logo.png") 
                await ctx.send(embed=mbed, view=view)

    @music.command(name="disconnect", description="ボイスチャンネルから退出", with_app_command=True)    
    async def leave_command(self, ctx:commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
        
        await player.disconnect()
        mbed = discord.Embed(title="ボイスチャンネルから退出", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @music.command(name="stop", description="停止", with_app_command=True)    
    async def stop_command(self, ctx:commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        
        if player is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
        
        if player.is_playing:
            player.queue.clear()
            await player.stop()
            mbed = discord.Embed(title="停止", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("現在音楽は流れていません")

    @music.command(name="skip", description="スキップ", with_app_command=True)    
    async def skip_command(self, ctx:commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        
        if player is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
            
        if player.is_playing:
            await player.stop()
            mbed = discord.Embed(title="スキップ", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("現在音楽は流れていません")

    @music.command(name="pause", description="一時停止", with_app_command=True)    
    async def pause_command(self, ctx:commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
            
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                mbed = discord.Embed(title="一時停止中", color=discord.Color.from_rgb(255, 255, 255))
                return await ctx.send(embed=mbed)
            else:
                return await ctx.send("現在音楽は流れていません")
        else:
            return await ctx.send("既に一時停止中です")

    @music.command(name="resume", description="再生", with_app_command=True)    
    async def resume_command(self, ctx:commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
            
        if player.is_paused():
            await player.resume()
            mbed = discord.Embed(title="再生中", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("音楽は一時停止されていません")

    @music.command(name="volume", description="ボリュームを変更します", with_app_command=True)    
    @app_commands.describe(volume="変更したい数値")
    async def volume_command(self, ctx:commands.Context, volume: int):
        vol=volume / 100
        if vol > 5:
            return await ctx.send("ボリュームは0~500の間で変更できます")
        elif vol < 0.001 :
            return await ctx.send("ボリュームは0~500の間で変更できます")
            
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
        else:
            await player.set_volume(vol)
            mbed = discord.Embed(title=f"ボリュームが {volume} に変更されました", color=discord.Color.from_rgb(255, 255, 255))
            await ctx.send(embed=mbed)

    @music.command(name="queue", description="キューを確認します", with_app_command=True)    
    async def queue_command(self, ctx:commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            return await ctx.send("キューに曲はありません")
        embed = discord.Embed(title="キュー", color=discord.Color.from_rgb(255, 255, 255))
        queue = vc.queue.copy()
        songCount = 0
        for song in queue:
            songCount += 1
            embed.add_field(name=f"No.{str(songCount)}", value=f"`{song}`")
        await ctx.send(embed=embed)

    @music.command(name="bassboost", description="低音をブーストします", with_app_command=True)    
    async def boost_command(self, ctx:commands.Context):
        vc: wavelink.Player = ctx.voice_client

        if vc is None:
            return await ctx.send("botがボイスチャンネルに接続していません")
        bands = [(0, 0.2), (1, 0.15), (2, 0.1), (3, 0.05), (4, 0.0),(5, -0.05), (6, -0.1), (7, -0.1), (8, -0.1), (9, -0.1),(10, -0.1), (11, -0.1), (12, -0.1), (13, -0.1), (14, -0.1)]
        await vc.set_filter(wavelink.Filter(equalizer=wavelink.Equalizer(name="MyOwnFilter",bands=bands)), seek=True)
        await ctx.send("ブースト開始")

    @music.command(name="removeboost", description="ブースト解除します", with_app_command=True)    
    async def rmvboost_command(self, ctx:commands.Context):
        vc: wavelink.Player = ctx.voice_client
        await vc.set_filter(wavelink.Filter(equalizer=wavelink.Equalizer.flat()),seek=True)
        await ctx.send("ブースト解除")

    @commands.hybrid_command(name="kodane", description="褒美だ.......", with_app_command=True)    
    async def kodane(self, ctx:commands.Context):
        search = "褒美だ。我の素材をくれてやる【GB素材】"
        track = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
            
        await vc.play(track)
        await ctx.send("褒美だ、我の子種をくれてやる。")
        await ctx.send("https://pbs.twimg.com/media/FK_tTvmaAAAYzMp.jpg")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))

   
    



    

    
