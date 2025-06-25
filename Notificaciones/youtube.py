import discord
import requests
import time
from discord.ext import tasks, commands
from googleapiclient.discovery import build

# Configuración de tu bot de Discord y YouTube
DISCORD_TOKEN = 'tu_token_de_discord'
YOUTUBE_API_KEY = 'tu_api_key_de_youtube'
YOUTUBE_CHANNEL_ID = 'tu_channel_id_de_youtube'
DISCORD_CHANNEL_ID = 123456789012345678  # ID del canal donde quieres enviar el mensaje

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Crear un cliente de la API de YouTube
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Función para obtener el último video subido
def get_last_video():
    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        order="date",
        maxResults=1
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]
    return None

# Enviar mensaje a Discord si hay un nuevo video
@tasks.loop(minutes=5)  # Comprobar cada 5 minutos
async def youtube_notification():
    last_video = get_last_video()
    if last_video:
        video_url = f"https://www.youtube.com/watch?v={last_video['id']['videoId']}"
        title = last_video['snippet']['title']
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(f"¡Nuevo video subido a YouTube! {title} [Ver aquí]({video_url})")

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    youtube_notification.start()  # Iniciar la comprobación periódica

bot.run(DISCORD_TOKEN)
