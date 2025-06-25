import discord

# IDs fijos, los podés pasar como parámetros si querés
CANAL_BIENVENIDA_ID = 1383604497829466124
ROL_USUARIO_ID = 1383593131340988477

def setup_welcome_events(bot):

    @bot.event
    async def on_member_join(member):
        canal = member.guild.get_channel(CANAL_BIENVENIDA_ID)
        rol = member.guild.get_role(ROL_USUARIO_ID)

        embed = discord.Embed(
            title="🎉 Bienvenido a la COMUNIDAD DESTURCTOR2_2ツ",
            description=(
                f"Hola, {member.mention} bienvenid@ a este servidor.\n\n"
                "En este servidor podrás divertirte y pasarlo bien con toda la comunidad.\n\n"
                "📜 No olvides leer las reglas en el canal de <#1386366313919811695>\n"
                "📰 Entérate de todas las noticias en el canal de <#1386368707109851186>\n"
                "💬 Pásate por el canal de <#1383604956740980797> para empezar a hablar con más gente.\n\n"
                "¡Espero que disfrutes y lo pases genial! 🥳"
            ),
            color=discord.Color.blurple()
        )
        embed.set_image(url="https://drive.google.com/uc?export=view&id=1GudzbrDA71XU540hY-I9SipHNQYnKlHO")

        if canal:
            await canal.send(embed=embed)
            print("✅ Mensaje de bienvenida enviado con imagen")

        bot_roles = [role.name for role in member.guild.me.roles]
        print(f"Roles del bot: {bot_roles}")

        if rol:
            try:
                await member.add_roles(rol)
                print(f"✅ Rol '{rol.name}' asignado a {member}")
            except discord.Forbidden:
                print("❌ No tengo permisos para asignar ese rol.")
            except Exception as e:
                print(f"❌ Error asignando rol: {e}")
        else:
            print("❌ No se encontró el rol de usuario.")
