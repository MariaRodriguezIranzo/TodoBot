import discord
import requests
import time
form discord.ext import task, commands

# Config
DISCORD_TOKEN = 'tu_token_de_discord'
TWITCH_CLIENT_ID = 'tu_client_id_de_twitch'
TWITCH_OAUTH_TOKEN = 'tu_oauth_token_de_twitch'
TWITCH_USER_NAME = 'tu_nombre_de_usuario_en_twitch'
DISCORD_CHANNEL_ID = 123456789012345678

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Comprobar si estás en directo en Twitch
def check_stream():
    url = f'https://api.twitch.tv/helix/streams?user_login={TWITCH_USER_NAME}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {TWITCH_OAUTH_TOKEN}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return True  # Está en directo
        else:
            return False  # No está en directo
    else:
        print(f'Error al consultar Twitch: {response.status_code}')
        return False

# Enviar mensaje a Discord si estás en directo
@tasks.loop(minutes=5)  # Comprobar cada 5 minutos
async def twitch_notification():
    if check_stream():
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(f'¡Estoy en directo en Twitch! [Ver aquí](https://www.twitch.tv/{TWITCH_USER_NAME})')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    twitch_notification.start()  # Iniciar la comprobación periódica

bot.run(DISCORD_TOKEN)