import discord
from discord.ext import commands
import os
import psycopg2
from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio


TOKEN = os.environ['DISCORD_TOKEN']

DATABASE_URL = os.environ['DATABASE_URL']

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Start!")
    while True:
        try:
            print("### Update all")
            await update_all()
            print("### Finish")
            await asyncio.sleep(900)
        except Exception as e:
            print(f"[Error] {e}")


# @bot.command(name="updateAll")
# async def update_all(ctx):
#     with psycopg2.connect(DATABASE_URL) as conn:
#         await update_all(conn)


@bot.command()
async def identify(ctx, name: str):
    if not get_color(name):
        await ctx.send("注意：そのようなAtCoderアカウントは見つかりません")
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                set_name(name, ctx.author, cur)
            conn.commit()
        print(f"{ctx.author.display_name}'s atcoder_name changed to: {name}")
        if not name.count("`"):
            await ctx.send(f"AtCoderユーザ名が `{name}` に変更されました")
        else:
            await ctx.send(f"AtCoderユーザ名が変更されました")
        color = get_color(name)
        if color and color != "unrated":
            await set_role(ctx.author, color)
    except Exception as e:
        await ctx.send(f"エラー：{e}")


async def update_all():
    for guild in bot.guilds:
        total = len(guild.members)
        for i, member in enumerate(guild.members):
            print(i, "/", total)
            if not member.bot:
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as cur:
                        name = get_name(member, cur)
                    conn.commit()
                color = get_color(name)
                if color and color != "unrated":
                    await set_role(member, color)


def get_name(member, cur):
    discord_name = f"{member.name}#{member.discriminator}"
    cur.execute("SELECT atcoder_name FROM profile "
                "WHERE discord_name = %s", (discord_name,))
    fetched = cur.fetchone()
    if fetched:
        atcoder_name = fetched[0]
    else:
        atcoder_name = member.display_name
        cur.execute("INSERT INTO profile (discord_name, atcoder_name, color) "
                    "VALUES (%s, %s, '')",
                    (discord_name, atcoder_name))
    return atcoder_name


def set_name(name, member, cur):
    discord_name = f"{member.name}#{member.discriminator}"
    print(discord_name)
    cur.execute("SELECT atcoder_name FROM profile "
                f"WHERE discord_name = %s", (discord_name,))
    fetched = cur.fetchone()
    if fetched:
        cur.execute(f"UPDATE profile SET atcoder_name = '{name}' "
                    f"WHERE discord_name = %s", (discord_name,))
    else:
        cur.execute("INSERT INTO profile (discord_name, atcoder_name, color) "
                    f"VALUES (%s, %s, '')", (discord_name, name))


def get_color(name):
    try:
        html = urlopen("https://atcoder.jp/users/" + name)
        soup = BeautifulSoup(html, "html.parser")
        span_tag = soup.find("a", class_="username").find("span")
        style = span_tag.get("class")[0]
        return style[5:]
    except:
        print(f"Invalid username: '{name}'")
        return None


async def set_role(member, color):
    print(f"Setting the role of {member.display_name} as {color} coder")
    roles = [role for role in member.guild.roles
             if role.name == color + " coder"]
    if roles:
        try:
            await member.edit(roles=roles)
            print("Set: " + ", ".join(role.name for role in roles))
        except discord.errors.Forbidden:
            print("Permission denied")
    else:
        print("[Bug] Role not found")


bot.run(TOKEN)
