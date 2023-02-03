import io
import os
import re
import zlib
from typing import  Generator, Optional
from .utils import fuzzy
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

RTFM_PAGE_TYPES = {
    'stable': 'https://discordpy.readthedocs.io/en/stable',
    'stable-jp': 'https://discordpy.readthedocs.io/ja/stable',
    'latest': 'https://discordpy.readthedocs.io/en/latest',
    'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
    'python': 'https://docs.python.org/3',
    'python-jp': 'https://docs.python.org/ja/3',
}

class SphinxObjectFileReader:
    BUFSIZE = 16 * 1024

    def __init__(self, buffer: bytes):
        self.stream = io.BytesIO(buffer)

    def readline(self) -> str:
        return self.stream.readline().decode('utf-8')

    def skipline(self) -> None:
        self.stream.readline()

    def read_compressed_chunks(self) -> Generator[bytes, None, None]:
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self) -> Generator[str, None, None]:
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1 :]
                pos = buf.find(b'\n')

class Docs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def finder(self, text, collection, *, key=None, lazy=True):
        suggestions = []
        text = str(text)
        pat = ".*?".join(map(re.escape, text))
        regex = re.compile(pat, flags=re.IGNORECASE)
        for item in collection:
            to_search = key(item) if key else item
            r = regex.search(to_search)
            if r:
                suggestions.append((len(r.group()), r.start(), item))

        def sort_key(tup):
            if key:
                return tup[0], tup[1], key(tup[2])
            return tup

        if lazy:
            return (z for _, _, z in sorted(suggestions, key=sort_key))
        else:
            return [z for _, _, z in sorted(suggestions, key=sort_key)]

    def parse_object_inv(self, stream: SphinxObjectFileReader, url: str):
        result = {}

        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                continue
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self):
        cache = {}
        for key, page in RTFM_PAGE_TYPES.items():
            cache[key] = {}
            async with aiohttp.ClientSession() as session:
                async with session.get(page + '/objects.inv') as resp:
                    if resp.status != 200:
                        raise RuntimeError('Cannot build rtfm lookup table, try again later.')

                    stream = SphinxObjectFileReader(await resp.read())
                    cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(self, ctx: commands.Context, key, obj: Optional[str]):
        if obj is None:
            await ctx.send(RTFM_PAGE_TYPES[key])
            return

        if not hasattr(self, '_rtfm_cache'):
            await ctx.typing()
            await self.build_rtfm_lookup_table()

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())
        matches = fuzzy.finder(obj, cache, key=lambda t: t[0])[:8]

        embed = discord.Embed(colour=0x05FFF0)
        embed.set_footer(text=f'{ctx.author}のリクエスト', icon_url=f'{ctx.author.avatar}')
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4403/4403455.png")
        if len(matches) == 0:
            return await ctx.send('見つかりませんでした。')

        embed.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
        await ctx.send(embed=embed)


    async def rtfm_slash_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:

        if not hasattr(self, '_rtfm_cache'):
            await interaction.response.autocomplete([])
            await self.build_rtfm_lookup_table()
            return []

        if not current:
            return []

        if len(current) < 3:
            return [app_commands.Choice(name=current, value=current)]

        assert interaction.command is not None
        key = interaction.command.name
        if key == 'jp':
            key = 'latest-jp'

        matches = fuzzy.finder(current, self._rtfm_cache[key])[:10]
        return [app_commands.Choice(name=m, value=m) for m in matches]

    @commands.Cog.listener()
    async def on_ready(self):
        print("Doc Cog is now ready!")

    
    @commands.hybrid_group(fallback='stable' , description="discord.py のドキュメントを参照します(英語版)")
    @app_commands.describe(entity='検索するオブジェクト名')
    @app_commands.autocomplete(entity=rtfm_slash_autocomplete)
    async def rtfm(self, ctx: commands.Context, *, entity: Optional[str] = None):
        await self.do_rtfm(ctx, 'stable', entity)

    @rtfm.command(name="jp", description="discord.py のドキュメントを参照します(日本語版)", with_app_command=True)
    @app_commands.describe(entity='検索するオブジェクト名')
    @app_commands.autocomplete(entity=rtfm_slash_autocomplete)
    async def rtfm_jp(self, ctx: commands.Context, *, entity: Optional[str] = None):
        await self.do_rtfm(ctx, 'latest-jp', entity)

    @rtfm.command(name="python", description="python のドキュメントを参照します(英語版)", with_app_command=True)
    @app_commands.describe(entity='検索するオブジェクト名')
    @app_commands.autocomplete(entity=rtfm_slash_autocomplete)
    async def rtfm_python(self, ctx: commands.Context, *, entity: Optional[str] = None):
        await self.do_rtfm(ctx, 'python', entity)

    @rtfm.command(name="python-jp", description="python のドキュメントを参照します(日本語版)", with_app_command=True)
    @app_commands.describe(entity='検索するオブジェクト名')
    @app_commands.autocomplete(entity=rtfm_slash_autocomplete)
    async def rtfm_python_jp(self, ctx: commands.Context, *, entity: Optional[str] = None):
        await self.do_rtfm(ctx, 'python-jp', entity)

    @rtfm.command(name="latest", description="discord.py のドキュメントを参照します(最新版)", with_app_command=True)
    @app_commands.describe(entity='検索するオブジェクト名')
    @app_commands.autocomplete(entity=rtfm_slash_autocomplete)
    async def rtfm_master(self, ctx: commands.Context, *, entity: Optional[str] = None):
        await self.do_rtfm(ctx, 'latest', entity)

    

async def setup(bot: commands.Bot):  
    await bot.add_cog(Docs(bot))