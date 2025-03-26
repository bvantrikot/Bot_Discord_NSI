import discord   # pip install discord
import random    
import asyncio   # pip install asyncio
import time
import pytz      # pip install pytz
import requests  # pip install requests
import icalendar # pip install icaneldar
import json
from discord.ext import commands
from datetime import datetime




TOKEN = 'TOKKEN DE VOTRE BOT' # mettre le token de votre bot
intents = discord.Intents.all()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)



with open("questions.json", "r", encoding="utf-8") as f: # mettre le chemin absolu du fichier /questions.json
    themes = json.load(f)
last_question_time = {}
rappels = {}



@bot.command(name='ping', help="Affiche la latence en millisecondes.")
async def ping_command(ctx):
    latence = round(bot.latency * 1000) 
    await ctx.send(f'Pong! Latence : {latence} ms')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="!help", url= "https://www.twitch.tv/c"))
    print("Bot connecté en tant que", bot.user.name)


last_question_time = {}

@bot.command(name='devinette', help ="Pour jouer à la devinette sur le programme de NSI !")
async def devinette(ctx):

    await ctx.send("Choisissez votre classe : Terminale (T) ou Première (P).")
    
    def check_classe(message):
        return message.author == ctx.author and message.content.upper() in ['T', 'P']

    try:
        classe_message = await bot.wait_for('message', check=check_classe, timeout=30.0)
        classe = classe_message.content.upper()
    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé. Vous n'avez pas choisi de classe.")
        return
    

    if classe == 'T':
        themes_list = list(themes["Terminale"].keys())
    elif classe == 'P':
        themes_list = list(themes["Première"].keys())
    
    theme_message = f"Choisissez un thème en tapant le numéro correspondant :\n"
    for i, theme in enumerate(themes_list, start=1):
        theme_message += f"{i}. {theme}\n"
    
    await ctx.send(theme_message)
    
    def check_theme(message):   
        return message.author == ctx.author and message.content.isdigit() and 1 <= int(message.content) <= len(themes_list)

    try:
        theme_message = await bot.wait_for('message', check=check_theme, timeout=30.0)
        selected_theme = themes_list[int(theme_message.content) - 1]
    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé. Vous n'avez pas choisi de thème.")
        return


    if classe == 'T':
        selected_question = random.choice(themes["Terminale"][selected_theme])
    elif classe == 'P':
        selected_question = random.choice(themes["Première"][selected_theme])


    await ctx.send(f"Question sur le thème '{selected_theme}':\n{selected_question['question']}\n"
                   "Choisissez la réponse en tapant la lettre correspondante (par exemple, 'a').")
    await ctx.send('\n'.join(selected_question["réponses"]))

    def check(message):
        return message.author == ctx.author

    try:
        réponse = await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé. La réponse correcte était : " +
                       ', '.join([r for r in selected_question["réponses"] if r.endswith(selected_question["correcte"])]) +
                       f" (Réponse {selected_question['correcte']})")

    else:
        if réponse.content.lower() == selected_question["correcte"].lower():
            await ctx.send("Bonne réponse !")
        else:
            await ctx.send("Mauvaise réponse. La réponse correcte était : " +
                           ', '.join([r for r in selected_question["réponses"] if r.endswith(selected_question["correcte"])]) +
                           f" (Réponse {selected_question['correcte']})")

    await ctx.send(f"Explication : {selected_question['explication']}")

    last_question_time[selected_question["question"]] = time.time()


@bot.command(name='serverinfo', help="Affiche des informations sur le serveur.")
async def serverinfo(ctx):
    server = ctx.guild
    total_members = server.member_count
    server_owner = server.owner
    creation_date = server.created_at.strftime('%d %B %Y')
    server_name = server.name

    embed = discord.Embed(
        title=f'Informations sur le serveur {server_name}',
        color=discord.Color.blue()
    )

    embed.add_field(name="Propriétaire du serveur", value=server_owner, inline=True)
    embed.add_field(name="Date de création", value=creation_date, inline=True)
    embed.add_field(name="Nombre de membres", value=total_members, inline=True)

    await ctx.send(embed=embed)

@bot.command(name='userinfo', help="Affiche des informations sur un utilisateur spécifique.")
async def userinfo(ctx, user: discord.Member):
    
    user_name = user.name
    user_id = user.id
    user_nick = user.nick
    user_roles = [role.name for role in user.roles[1:]]  # Exclude @everyone role
    user_creation_date = user.created_at.strftime('%d %B %Y')

    embed = discord.Embed(
        title=f'Informations sur {user_name}',
        color=discord.Color.green()
    )

    embed.add_field(name="Pseudo", value=user_name, inline=True)
    embed.add_field(name="Surnom", value=user_nick, inline=True)
    embed.add_field(name="ID de l'utilisateur", value=user_id, inline=True)
    embed.add_field(name="Rôles", value=', '.join(user_roles), inline=False)
    embed.add_field(name="Date de création du compte", value=user_creation_date, inline=False)

    await ctx.send(embed=embed)

last_response_time = 0
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        await message.channel.send(f"{message.author.mention} mon prefix est '!'.")

    global last_response_time
    current_time = time.time()

    if "quoi" in message.content.lower() and (current_time - last_response_time) >= 3600:
        await message.channel.send("feur")
        last_response_time = current_time

    await bot.process_commands(message)




@bot.command(name='rappelmoi', help="Permet aux utilisateurs de définir des rappels pour des événements futurs.")
async def rappelmoi(ctx, *, reminder : str = None):
    if reminder is None:
        await ctx.send("Veuillez spécifier le nom du rappel après la commande, séparé par un espace. Exemple : !rappelmoi MonRappel ")
        return
    await ctx.send("Quand souhaitez-vous être rappelé ? Veuillez spécifier la date et éventuellement l'heure (ex: '31/12/2023 15:30').")

    def check_time(message):
        try:
            datetime.strptime(message.content, '%d/%m/%Y %H:%M')
            return True
        except ValueError:
            return False

    try:
        time_message = await bot.wait_for('message', check=check_time, timeout=300.0)
        reminder_time = datetime.strptime(time_message.content, '%d/%m/%Y %H:%M')
    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé. Le rappel n'a pas été défini.")
        return

    current_time = datetime.now()
    time_difference = (reminder_time - current_time).total_seconds()

    if time_difference <= 0:
        await ctx.send("La date et l'heure du rappel sont dans le passé. Veuillez spécifier une date et une heure futures.")
        return

    await ctx.send(f"Je vous rappellerai de '{reminder}' le {reminder_time.strftime('%Y-%m-%d')} à {reminder_time.strftime('%H:%M')}.")

    if ctx.author.id not in rappels:
        rappels[ctx.author.id] = []

    rappels[ctx.author.id].append((reminder, reminder_time))

    await asyncio.sleep(time_difference)
    await ctx.send(f"{ctx.author.mention}, il est temps pour votre rappel : '{reminder}'")


@bot.command(name='listrappels', help="Affiche la liste des rappels programmés.")
async def listrappels(ctx):
    if ctx.author.id in rappels and rappels[ctx.author.id]:
        reminder_list = []
        for reminder, time in rappels[ctx.author.id]:
            reminder_list.append(f"Rappel de '{reminder}' à {time.strftime('%d-%m-%Y %H:%M')}")
        await ctx.send("Vos rappels programmés : \n" + "\n".join(reminder_list))
    else:
        await ctx.send("Vous n'avez pas de rappels programmés.")

@bot.command(name='deleterappel', help="Supprime un rappel spécifique.")
async def deleterappel(ctx, index: int):
    if ctx.author.id in rappels and 1 <= index <= len(rappels[ctx.author.id]):
        deleted_reminder = rappels[ctx.author.id].pop(index - 1)
        await ctx.send(f"Rappel supprimé : '{deleted_reminder[0]}' à {deleted_reminder[1].strftime('%d-%m-%Y %H:%M')}")
    else:
        await ctx.send("Rappel introuvable. Veuillez spécifier un numéro de rappel valide.")




@bot.command(name='vote', help="Lance un vote avec des options définies par l'utilisateur. Utilisation : !vote <durée_en_secondes> Option1 Option2 ...")
async def vote_command(ctx, *args):
    if len(args) < 3:
        await ctx.send("Utilisation incorrecte.\nFormat attendu : `!vote <durée_en_secondes> Option1 Option2 ...`\nExemple : `!vote 30 Pizza Sushi Tacos`")
        return

    try:
        duree_vote = int(args[0])
    except ValueError:
        await ctx.send("La première valeur doit être une durée en secondes (nombre entier).")
        return

    options = args[1:]
    if len(options) < 2:
        await ctx.send("Vous devez fournir au moins deux options pour le vote.")
        return

    if duree_vote <= 0:
        await ctx.send("La durée du vote doit être un nombre supérieur à 0.")
        return
    vote_message = f"Vote en cours pendant {duree_vote} secondes !\n\nOptions : {' | '.join(options)}\n\nRéagissez avec l'emoji correspondant à votre choix."

    vote_msg = await ctx.send(vote_message)

    for i in range(len(options)):
        emoji = chr(127462 + i)
        await vote_msg.add_reaction(emoji)

    await asyncio.sleep(duree_vote)

    vote_msg = await ctx.channel.fetch_message(vote_msg.id)

    reactions = vote_msg.reactions
    sorted_reactions = sorted(reactions, key=lambda r: r.count, reverse=True)


    if sorted_reactions:
        gagnante_emoji = sorted_reactions[0].emoji
        gagnante_option = options[ord(gagnante_emoji) - 127462]
        await ctx.send(f"Le vote est clos ! L'option gagnante est : {gagnante_option} avec {sorted_reactions[0].count - 1} votes.")
    else:
        await ctx.send("Le vote est clos, mais aucune réaction n'a été enregistrée. Aucune option n'a remporté la majorité.")





@bot.command(name='vacances', help="Affiche les dates des vacances scolaires dans l'académie de Versailles.")
async def vacances(ctx, annee: int = None):
    url = "https://fr.ftp.opendatasoft.com/openscol/fr-en-calendrier-scolaire/Zone-C.ics"

    try:
        response = requests.get(url)
        response.raise_for_status()

        cal_data = response.content
        cal = icalendar.Calendar.from_ical(cal_data)

        if annee is None:
            await ctx.send("Veuillez spécifier une année après la commande. Exemple : `!vacances 2025`")
            return

        vacances_par_annee = []

        for event in cal.walk('vevent'):
            start_date = event.get('dtstart').dt
            end_date = event.get('dtend').dt

            if isinstance(start_date, datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime):
                end_date = end_date.date()

            if start_date.year == annee or end_date.year == annee:
                vacances_par_annee.append((start_date, end_date))

        if vacances_par_annee:
            message = f"Vacances scolaires dans l'académie de Versailles pour l'année {annee} :\n"
            for start_date, end_date in vacances_par_annee:
                message += f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}\n"
        else:
            message = f"Aucune donnée de vacances trouvée pour l'année {annee}."

        await ctx.send(message)

    except requests.exceptions.HTTPError as errh:
        await ctx.send(f"Erreur HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        await ctx.send(f"Erreur de connexion: {errc}")
    except requests.exceptions.Timeout as errt:
        await ctx.send(f"Erreur de timeout: {errt}")
    except requests.exceptions.RequestException as err:
        await ctx.send(f"Une erreur s'est produite : {err}")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {e}")


@bot.command(name='joursferies', help="Affiche les jours fériés dans l'académie de Versailles.")
async def jours_feries(ctx, annee: int = None):
    url = "https://etalab.github.io/jours-feries-france-data/ics/jours_feries_metropole.ics"

    try:
        response = requests.get(url)
        response.raise_for_status()

        cal_data = response.content
        cal = icalendar.Calendar.from_ical(cal_data)

        if annee is None:
            await ctx.send("Veuillez spécifier une année après la commande. Exemple : `!joursferies 2025`")
            return

        feries_par_annee = []

        for event in cal.walk('vevent'):
            start_date = event.get('dtstart').dt

            if isinstance(start_date, datetime):
                start_date = start_date.date()

            if start_date.year == annee:
                summary = event.get('summary')
                feries_par_annee.append((start_date, summary))

        if feries_par_annee:
            message = f"Jours fériés en {annee} :\n"
            for date, summary in feries_par_annee:
                message += f"{date.strftime('%d/%m/%Y')} - {summary}\n"
        else:
            message = f"Aucun jour férié trouvé pour l'année {annee}."

        await ctx.send(message)

    except requests.exceptions.HTTPError as errh:
        await ctx.send(f"Erreur HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        await ctx.send(f"Erreur de connexion: {errc}")
    except requests.exceptions.Timeout as errt:
        await ctx.send(f"Erreur de timeout: {errt}")
    except requests.exceptions.RequestException as err:
        await ctx.send(f"Une erreur s'est produite : {err}")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {e}")



bot.run(TOKEN)
