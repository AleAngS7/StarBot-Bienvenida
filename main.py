import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import random
from keep_alive import keep_alive
import os

keep_alive()

CANAL_BIENVENIDA_ID = 1352152658059857941
CANAL_DESPEDIDA_ID = 1352152885613559858
CANAL_BAN_ID = 1401658312973619201


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member):
    fondo = Image.open("fond.png").convert("RGBA")
    ancho_img, alto_img = fondo.size

    # Descargar avatar
    avatar_url = member.avatar.replace(size=512, format="png").url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA")

    # Tamaño del avatar más grande para imágenes grandes
    avatar_size = int(ancho_img * 0.24)  # 28% del ancho
    avatar = avatar.resize((avatar_size, avatar_size))

    # Crear máscara circular
    mask = Image.new("L", avatar.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    avatar_circular = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar_circular.putalpha(mask)

    # Crear marco redondo (borde)
    borde_blanco = int(avatar_size * 0.025)
    borde_sombra = int(avatar_size * 0.005)

    tamaño_total = avatar_size + 2 * (borde_blanco + borde_sombra)

    # Desplazamiento de la sombra (negativo x para izquierda, positivo y para abajo)
    offset_x_sombra = -int(borde_sombra * -2.4)
    offset_y_sombra = int(borde_sombra * 2.4)

    canvas_width = tamaño_total + abs(offset_x_sombra)
    canvas_height = tamaño_total + offset_y_sombra

    avatar_con_sombra = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(avatar_con_sombra)

    # Dibujar círculo negro sombra desplazado
    pos_sombra = (offset_x_sombra if offset_x_sombra >= 0 else 0,
                  offset_y_sombra if offset_y_sombra >= 0 else 0)
    draw.ellipse(
        (
            pos_sombra[0],
            pos_sombra[1],
            pos_sombra[0] + tamaño_total,
            pos_sombra[1] + tamaño_total,
        ),
        fill=(0, 0, 0, 255),
    )

    # Dibujar borde blanco
    offset_blanco = borde_sombra
    diametro_blanco = tamaño_total - 2 * offset_blanco
    draw.ellipse(
    (offset_blanco, offset_blanco, offset_blanco + diametro_blanco, offset_blanco + diametro_blanco),
        fill=(255, 255, 255, 255),
    )

    # Pegar avatar circular en centro del borde blanco
    offset_avatar = borde_sombra + borde_blanco
    avatar_con_sombra.paste(avatar_circular, (offset_avatar, offset_avatar), avatar_circular)

    # Posicionar avatar centrado un poco más abajo
    x_avatar = (ancho_img - tamaño_total) // 2
    y_avatar = int(alto_img * 0.15)  # Ajustado para dejar más espacio arriba

    fondo.paste(avatar_con_sombra, (x_avatar, y_avatar), avatar_con_sombra)

    # Crear objeto draw
    draw = ImageDraw.Draw(fondo)

    # Mensajes de bienvenida
    saludos = [
        "¡Hola {nombre}!",
        "¡Saludos, {nombre}!",
        "¡{nombre} ha llegado!",
        "¡Buenas {nombre}!",
        "¡Hey {nombre}!",
        "¡Que tal {nombre}!",
    ]

    bienvenidas = [
        "¡Te damos la bienvenida!",
        "¡Gracias por unirte!",
        "¡Nos alegra verte por aqui!",
        "¡Esperamos que te diviertas!",
        "¡Un gusto contar contigo!",
        "¡Ve y conoce a todos!",
        "¡Adentrate y diviertete!",
        "¡La comunidad te espera!",
        "¡Disfruta tu estadia!",
        "¡Que la pases bien!",
    ]

    # Texto
    texto1 = random.choice(saludos).format(nombre=member.name)
    texto2 = random.choice(bienvenidas)


    fuente_path = "mine.otf"
    tamaño_base = int(ancho_img * 0.06)  # Más grande
    fuente1 = ImageFont.truetype(fuente_path, tamaño_base)
    fuente2 = ImageFont.truetype(fuente_path, int(tamaño_base * 0.6))

    # Medir y centrar texto1
    bbox1 = draw.textbbox((0, 0), texto1, font=fuente1)
    ancho_texto1 = bbox1[2] - bbox1[0]
    alto_texto1 = bbox1[3] - bbox1[1]
    x_texto1 = (ancho_img - ancho_texto1) // 2
    y_texto1 = y_avatar + tamaño_total + int(alto_img * 0.03)

    # Sombra para texto1
    sombra_offset = int(tamaño_base * 0.05)
    draw.text((x_texto1 + sombra_offset, y_texto1 + sombra_offset), texto1, font=fuente1, fill=(0, 0, 0, 150))

    # Texto 1
    draw.text((x_texto1, y_texto1), texto1, font=fuente1, fill=(255, 255, 255))

    # Medir y centrar texto2
    bbox2 = draw.textbbox((0, 0), texto2, font=fuente2)
    ancho_texto2 = bbox2[2] - bbox2[0]
    x_texto2 = (ancho_img - ancho_texto2) // 2
    y_texto2 = y_texto1 + alto_texto1 + int(alto_img * 0.02)

    # Sombra para texto2
    draw.text((x_texto2 + sombra_offset, y_texto2 + sombra_offset), texto2, font=fuente2, fill=(0, 0, 0, 150))

    # Texto 2
    draw.text((x_texto2, y_texto2), texto2, font=fuente2, fill=(200, 200, 200))

    # Guardar y enviar imagen
    fondo.save("bienvenida.png")
    canal = member.guild.get_channel(CANAL_BIENVENIDA_ID)  # ← tu ID de canal aquí
    if canal:
        # Crear archivo y objeto File
        archivo = discord.File("bienvenida.png", filename="bienvenida.png")

        # Crear embed

        # Elegir titulo aleatorio
        titulos = [
            "¡{nombre} ha llegado!",
            "¡Denle la bienvenida a {nombre}!",
            "¡{nombre} se ha unido a la tripulación!",
            "¡{nombre} se ha unido a nosotros!",
            "¡Un fuerte saludo para {nombre}!",
            "¡Nueva energía en el servidor: {nombre}!",
        ]

        titulo = random.choice(titulos).format(nombre=member.name)
        frases_bienvenida = [
            "¡Te damos la bienvenida al servidor {user}!",
            "¡Un gusto tenerte aquí, {user}!",
            "¡Qué alegría que te unas, {user}!",
            "¡Bienvenido a bordo, {user}!",
        ]

        # Descripcion aleatoria
        frases_esperanza = [
            "Esperamos que lo pases increíble aquí <:emoji_7:1357165067069554788>",
            "Confíamos en que disfrutarás tu estancia <:emoji_7:1357165067069554788>",
            "¡Que tu experiencia aquí sea positiva y divertida! <:emoji_7:1357165067069554788>",
        ]

        frases_final = [
            "Prepárate para la aventura <a:Baby:1364261003944136744>",
            "¡Explora, conoce y diviértete! <a:Baby:1364261003944136744>",
            "¡Comienza tu viaje ahora! <a:Baby:1364261003944136744>",
        ]

        # Elegir una frase de cada grupo
        linea1 = random.choice(frases_bienvenida).format(user=member.mention)
        linea2 = random.choice(frases_esperanza)
        linea3 = random.choice(frases_final)

        # Texto fijo
        linea_rules = "<a:Target:1357186717060432045> ¡Asegúrate de revisar la <id:home>\n📜 Y de leer las <#1351290702755270881> antes de comenzar! <:discord:1357189861689266307>"

        linea_soporte = "-#  Si tienes dudas, el equipo de moderación está disponible <:Soporte:1369748445203796140>"

        # Combinar todas las líneas
        descripcion_embed = f"{linea1}\n\n{linea2}\n\n{linea_rules}\n\n{linea3}\n\n{linea_soporte}"

        # Crear embed
        embed = discord.Embed(
            title=titulo,
            url="https://discord.com/channels/1351275685343133696/1351290702755270881/1354695965243609188",  # ← aquí va la URL que quieres enlazar
            description=descripcion_embed,
            color=discord.Color.from_str("#5e41b1")
        )

        # Insertar imagen en el embed
        embed.set_image(url="attachment://bienvenida.png")
        embed.set_thumbnail(url=bot.user.avatar.url)  # o cualquier URL válida

        # Pie de página y timestamp
        embed.set_footer(text=f"Ahora somos {len(member.guild.members)} miembros 👥")
        embed.timestamp = discord.utils.utcnow()

        # Enviar embed con imagen
        # await canal.send(file=archivo, embed=embed)
        # Enviar el mensaje y guardar el mensaje enviado
        mensaje = await canal.send(embed=embed, file=archivo)
        # Reaccionar automáticamente (puedes poner más de uno si quieres)
        #await mensaje.add_reaction("👋")  # Saludo
        await mensaje.add_reaction("<a:Wave:1364260987321974835>")  # Personalizado


@bot.event
async def on_member_remove(member):
    canal = member.guild.get_channel(CANAL_BAN_ID)  # Tu canal

    if not canal:
        print("❌ Canal no encontrado.")
        return

    # Verificar si fue kick o ban
    async for entry in member.guild.audit_logs(limit=10):
        time_difference = datetime.now(timezone.utc) - entry.created_at
        if time_difference > timedelta(seconds=10):
            continue  # Saltar si es muy viejo

        if entry.action == discord.AuditLogAction.ban and entry.target.id == member.id:
            # ❌ Fue baneado → cancelar la acción
            print(f"[LOG] {member.name} fue baneado. No se enviará ningún mensaje.")
            return

        if entry.action == discord.AuditLogAction.kick and entry.target.id == member.id:
            # 🔴 Fue kickeado → enviar embed de expulsión
            # Títulos de despedida para kick (neutros e inclusivos)
            titulos_kick = [
                "🦮 Le llevaron de paseo a {nombre}",
                "🏃‍♂️ {nombre} tuvo que salir del servidor",
                "⚠️ {nombre} recibió una pausa temporal",
                "🚪 Puerta cerrada para {nombre} (por ahora)",
                "⛔ {nombre} está fuera por un tiempo",
                "🔄 {nombre} tendrá que volver más tarde",
            ]
            
            titulo_kick = random.choice(titulos_kick).format(nombre=member.name)

            # Frases para acompañar el kick, estilo Minecraft (lenguaje neutral)
            frases_kick = [
                "Si regresa, deberá seguir correctamente la <id:home> y las https://discord.com/channels/1351275685343133696/1351290702755270881 establecidas.",
                "{nombre} tendrá que recolectar sus cosas fuera del servidor.",
                "Un descanso forzado para {nombre}, ¡esperamos que vuelva pronto!",
                "Los bloques se detuvieron para {nombre}, pero la aventura continúa.",
                "A veces hay que tomarse un respiro, {nombre}. ¡Nos vemos luego!",
                "El portal se cerró para {nombre}, pero la puerta sigue abierta.",
            ]

            
            linea_kick = random.choice(frases_kick).format(nombre=member.name)

            descripcion_kick = f"{linea_kick}"
            
            embed = discord.Embed(
                title=titulo_kick,
                description=descripcion_kick,
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Ahora somos {len(member.guild.members)} miembros 👥")
            embed.timestamp = discord.utils.utcnow()
            await canal.send(embed=embed)
            return

    # ✅ No fue kick ni ban → ejecutar despedida con imagen
    await despedida_con_imagen(member, canal)

async def despedida_con_imagen(member, canal):
    fondo = Image.open("fondo.png").convert("RGBA")
    ancho_img, alto_img = fondo.size
    # Descargar avatar
    avatar_url = member.avatar.replace(size=512, format="png").url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA")

    # Tamaño del avatar más grande para imágenes grandes
    avatar_size = int(ancho_img * 0.24)  # 28% del ancho
    avatar = avatar.resize((avatar_size, avatar_size))

    # Crear máscara circular
    mask = Image.new("L", avatar.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    avatar_circular = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar_circular.putalpha(mask)

    # Crear marco redondo (borde)
    borde_blanco = int(avatar_size * 0.025)
    borde_sombra = int(avatar_size * 0.005)

    tamaño_total = avatar_size + 2 * (borde_blanco + borde_sombra)

    # Desplazamiento de la sombra (negativo x para izquierda, positivo y para abajo)
    offset_x_sombra = -int(borde_sombra * -2.4)
    offset_y_sombra = int(borde_sombra * 2.4)

    canvas_width = tamaño_total + abs(offset_x_sombra)
    canvas_height = tamaño_total + offset_y_sombra

    avatar_con_sombra = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(avatar_con_sombra)

    # Dibujar círculo negro sombra desplazado
    pos_sombra = (offset_x_sombra if offset_x_sombra >= 0 else 0,
                  offset_y_sombra if offset_y_sombra >= 0 else 0)
    draw.ellipse(
        (
            pos_sombra[0],
            pos_sombra[1],
            pos_sombra[0] + tamaño_total,
            pos_sombra[1] + tamaño_total,
        ),
        fill=(0, 0, 0, 255),
    )

    # Dibujar borde blanco
    offset_blanco = borde_sombra
    diametro_blanco = tamaño_total - 2 * offset_blanco
    draw.ellipse(
    (offset_blanco, offset_blanco, offset_blanco + diametro_blanco, offset_blanco + diametro_blanco),
        fill=(255, 255, 255, 255),
    )

    # Pegar avatar circular en centro del borde blanco
    offset_avatar = borde_sombra + borde_blanco
    avatar_con_sombra.paste(avatar_circular, (offset_avatar, offset_avatar), avatar_circular)

    # Posicionar avatar centrado un poco más abajo
    x_avatar = (ancho_img - tamaño_total) // 2
    y_avatar = int(alto_img * 0.15)  # Ajustado para dejar más espacio arriba

    fondo.paste(avatar_con_sombra, (x_avatar, y_avatar), avatar_con_sombra)

    # Crear objeto draw
    draw = ImageDraw.Draw(fondo)

    # Mensajes de despedida
    salidas = [
        "¡Hasta luego, {nombre}!",
        "¡Adiós, {nombre}!",
        "¡Cuídate, {nombre}!",
        "¡Se fue {nombre}!",
        "¡{nombre} se retiro!",
    ]

    despedidas = [
        "¡Esperamos verte de nuevo!",
        "¡Fue un gusto tenerte aquí!",
        "¡Hasta la próxima aventura!",
        "¡Sigue brillando!",
        "¡Nos veremos en otra ocasion!",
        "¡Te extrañaremos!",
        "¡Una pena que te vayas!",
        "¡Sigue minando!",
        "¡Construye con cuidado!",
    ]


    # Texto
    texto1 = random.choice(salidas).format(nombre=member.name)
    texto2 = random.choice(despedidas)


    fuente_path = "mine.otf"
    tamaño_base = int(ancho_img * 0.06)  # Más grande
    fuente1 = ImageFont.truetype(fuente_path, tamaño_base)
    fuente2 = ImageFont.truetype(fuente_path, int(tamaño_base * 0.6))

    # Medir y centrar texto1
    bbox1 = draw.textbbox((0, 0), texto1, font=fuente1)
    ancho_texto1 = bbox1[2] - bbox1[0]
    alto_texto1 = bbox1[3] - bbox1[1]
    x_texto1 = (ancho_img - ancho_texto1) // 2
    y_texto1 = y_avatar + tamaño_total + int(alto_img * 0.03)

    # Sombra para texto1
    sombra_offset = int(tamaño_base * 0.05)
    draw.text((x_texto1 + sombra_offset, y_texto1 + sombra_offset), texto1, font=fuente1, fill=(0, 0, 0, 150))

    # Texto 1
    draw.text((x_texto1, y_texto1), texto1, font=fuente1, fill=(255, 255, 255))

    # Medir y centrar texto2
    bbox2 = draw.textbbox((0, 0), texto2, font=fuente2)
    ancho_texto2 = bbox2[2] - bbox2[0]
    x_texto2 = (ancho_img - ancho_texto2) // 2
    y_texto2 = y_texto1 + alto_texto1 + int(alto_img * 0.02)

    # Sombra para texto2
    draw.text((x_texto2 + sombra_offset, y_texto2 + sombra_offset), texto2, font=fuente2, fill=(0, 0, 0, 150))

    # Texto 2
    draw.text((x_texto2, y_texto2), texto2, font=fuente2, fill=(200, 200, 200))

    # Guardar y enviar imagen
    fondo.save("despedida.png")
    canal = member.guild.get_channel(CANAL_DESPEDIDA_ID)  # ← tu ID de canal aquí
    if canal:
        # Crear archivo y objeto File
        archivo = discord.File("despedida.png", filename="despedida.png")

        # Crear embed

        # Elegir titulo aleatorio
        titulos_despedida = [
            "¡Nos vemos pronto, {nombre}!",
            "¡{nombre} se ha desconectado!",
            "¡{nombre}, vuelve pronto!",
            "!Nos despedimos de {nombre}!",
            "¡{nombre} se desconectó!",
        ]



        titulo = random.choice(titulos_despedida).format(nombre=member.name)
        frases_despedida = [
            "Esperamos que su paso por aquí haya sido agradable y sus caminos lo lleven a nuevas aventuras :chibipirrot:",
            "Gracias por tu paso por el servidor, que siempre tengas bloques para construir grandes historias",
            "Te deseamos que tus caminos estén llenos de diamantes y tus noches sin creepers",
            "Gracias por ser parte de esta comunidad, que tu próximo viaje esté lleno de sorpresas y logros",
        ]

        # Descripcion aleatoria
        # frases_esperanza = [
            #"Esperamos que lo pases increíble aquí <:emoji_7:1357165067069554788>",
            #"Confíamos en que disfrutarás tu estancia <:emoji_7:1357165067069554788>",
            #"¡Que tu experiencia aquí sea positiva y divertida! <:emoji_7:1357165067069554788>",
        #]

        # frases_final = [
            #"Prepárate para la aventura <a:baby_toom:1369756014580207617>",
            #"¡Explora, conoce y diviértete! <a:baby_toom:1369756014580207617>",
            #"¡Comienza tu viaje ahora! <a:baby_toom:1369756014580207617>",
        #]

        # Elegir una frase de cada grupo
        linea1 = random.choice(frases_despedida).format(user=member.mention)
        # linea2 = random.choice(frases_esperanza)
        # linea3 = random.choice(frases_final)

        # Texto fijo
        # linea_rules = "📌 ¡Asegúrate de revisar las <id:home>\n📄 Lee las [reglas aquí](https://discord.com/channels/1351275685343133696/1351290702755270881) <:Discord:1369755864067473540>"

        # linea_soporte = "-#  Si tienes dudas, el equipo de moderación está disponible <:Soporte:1369755750712348713>"

        # Combinar todas las líneas
        # descripcion_embed = f"{linea1}\n\n{linea2}\n\n{linea_rules}\n\n{linea3}\n\n{linea_soporte}"
        descripcion_embed = f"{linea1}" # \n\n{linea2}\n\n{linea_rules}\n\n{linea3}\n\n{linea_soporte}"

        # Crear embed
        embed = discord.Embed(
            title=titulo,
            url="https://discord.com/channels/1351275685343133696/1352152885613559858",  # ← aquí va la URL que quieres enlazar
            description=descripcion_embed,
            color=discord.Color.from_str("#5e41b1")
        )

        # Insertar imagen en el embed
        embed.set_image(url="attachment://despedida.png")
        embed.set_thumbnail(url=bot.user.avatar.url)  # o cualquier URL válida

        # Pie de página y timestamp
        embed.set_footer(text=f"Ahora somos {len(member.guild.members)} miembros 👥")
        embed.timestamp = discord.utils.utcnow()

        # Enviar embed con imagen
        # await canal.send(file=archivo, embed=embed)
        # Enviar el mensaje y guardar el mensaje enviado
        mensaje = await canal.send(embed=embed, file=archivo)
        # Reaccionar automáticamente (puedes poner más de uno si quieres)
        await mensaje.add_reaction("👋")  # Saludo
        #await mensaje.add_reaction("<:emoji_1:1360992508368130229>")  # Personalizado


@bot.event
async def on_member_ban(guild, user):
    canal = guild.get_channel(1401658312973619201)  # ← tu ID de canal aquí
    if not canal:
        return

    try:
        ban_entry = await guild.fetch_ban(user)
        razon = ban_entry.reason or "Sin razón específica."
    except Exception as e:
        razon = "No se pudo obtener la razón del ban."

    # Títulos de despedida para ban
    titulos_ban = [
        "🚫 Le dieron ban a {nombre}",
        "⚫️ {nombre} cayó al vacío",
        "⚠️ {nombre} ya no esá entre nosotros",
        "🛑 Se ha tomado acción contra {nombre}",
    ]
    titulo = random.choice(titulos_ban).format(nombre=user.name)

    # Frases para acompañar el ban, estilo Minecraft
    #frases_ban = [
        #"Incluso en el mundo cúbico, las reglas importan.",
        #"El viaje de {nombre} terminó antes del siguiente amanecer.",
        #"Sus bloques quedarán atrás, pero la lección permanece.",
        #"Toda aventura tiene un final... a veces forzado.",
        #"Que aprenda del exilio y regrese más sabio (si es que vuelve).",
        #"Sus días de construcción aquí han terminado.",
    #]
    #linea_contexto = random.choice(frases_ban).format(nombre=user.name)

    descripcion_embed = f"**Razón:** {razon}"

    # Crear embed
    embed = discord.Embed(
        title=titulo,
        description=descripcion_embed,
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text=f"Miembros restantes: {len(guild.members)} 👥")
    embed.timestamp = discord.utils.utcnow()

    mensaje = await canal.send(embed=embed)
    await mensaje.add_reaction("<:IMG_6137:1377786630844186675>")
    await mensaje.add_reaction("<:IMG_7199:1377785673569800253>")
    #await mensaje.add_reaction("<:IMG_6137:1377786630844186675>")


# Ejecutar el bot
bot.run(os.getenv("DISCORD_TOKEN"))
