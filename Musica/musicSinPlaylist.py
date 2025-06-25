import discord
from discord.ext import commands
import asyncio
import yt_dlp
from youtubesearchpython import VideosSearch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# Configura tus credenciales de Spotify aquí
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="08667a4fc2a94060a86e96b4022e5024",
    client_secret="0e3d0e6d0ff24aa88ec386a1a4e9d913"
))

music_queue = []

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if data is None:
            raise Exception("No se pudo obtener información del video.")
        
        if 'entries' in data:
            data = data['entries'][0]

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

def setup_music_commands(bot):

    async def play_next(ctx):
        if music_queue:
            next_url = music_queue.pop(0)
            player = await YTDLSource.from_url(next_url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
            await ctx.send(f"🎶 Ahora suena: **{player.title}**")

    @bot.command(name="play")
    async def play(ctx, *, search_query: str):
        if not ctx.author.voice:
            await ctx.send("❌ Tienes que estar en un canal de voz.")
            return

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        await ctx.send(f"🔎 Buscando: `{search_query}`...")

        # Detectar si es un enlace de Spotify
        if "open.spotify.com/track" in search_query:
            try:
                match = re.search(r"track/([a-zA-Z0-9]+)", search_query)
                track_id = match.group(1)
                track_info = sp.track(track_id)
                search_query = f"{track_info['name']} {track_info['artists'][0]['name']}"
                await ctx.send(f"🎵 Buscando en YouTube: `{search_query}`")
            except Exception as e:
                await ctx.send("❌ No pude obtener la canción de Spotify.")
                print(e)
                return

        try:
            # Buscar en YouTube
            if not search_query.startswith("http"):
                videos_search = VideosSearch(search_query, limit=1)
                result = videos_search.result()
                if len(result['result']) == 0:
                    await ctx.send("❌ No encontré ningún resultado.")
                    return
                youtube_url = result['result'][0]['link']
            else:
                youtube_url = search_query

            if ctx.voice_client.is_playing():
                music_queue.append(youtube_url)
                await ctx.send("➕ Añadido a la cola.")
            else:
                player = await YTDLSource.from_url(youtube_url, loop=bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
                await ctx.send(f"🎶 Reproduciendo: **{player.title}**")

        except Exception as e:
            print(f"Error en play: {e}")
            await ctx.send("❌ Hubo un error al intentar reproducir la canción.")

    @bot.command(name="queue")
    async def queue(ctx):
        if not music_queue:
            await ctx.send("📭 La cola está vacía.")
        else:
            msg = "\n".join([f"{idx+1}. {url}" for idx, url in enumerate(music_queue)])
            await ctx.send(f"📃 Cola de canciones:\n{msg}")

    @bot.command(name="skip")
    async def skip(ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭ Canción saltada.")
        else:
            await ctx.send("❌ No hay música sonando.")

    @bot.command(name="stop")
    async def stop(ctx):
        if ctx.voice_client:
            music_queue.clear()
            await ctx.voice_client.disconnect()
            await ctx.send("🛑 Música detenida y cola vacía.")
        else:
            await ctx.send("❌ No estoy en ningún canal de voz.")