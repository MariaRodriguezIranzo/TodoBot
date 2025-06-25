import discord
from discord.ext import commands
from Bienvenida.welcome_role import setup_welcome_events
from Musica.music import setup_music_commands


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ TodoBot conectado como {bot.user}")

# Configuramos los eventos de bienvenida desde el módulo externo
setup_welcome_events(bot)
setup_music_commands(bot)

bot.run("MTM4NDU0MTMyNjMyMTY1MTcxMw.GB7JD3.OMTvz_04LFO_GpoUkQcWKLSgnhy_mXryKgNDAk")