import discord
from discord.ext import commands
import os
import psycopg2
from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime, timedelta


TOKEN = 'Njg1MTU0MjM0OTE5OTQ0MjE5.XmGnBA.N6r9yyCPtxH2Iuazod12u9eQbcA'

DATABASE_URL = os.environ['DATABASE_URL']

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Start!")
    now = datetime.now()
    wait_for = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
    print("Update scheduled at " + str(wait_for))
    await asyncio.sleep((wait_for - now).total_seconds())
    while True:
        with psycopg2.connect(DATABASE_URL) as conn:
            print("### Update all")
            await update_all(conn)
            print("### Finished")
        await asyncio.sleep(86400)


# @bot.command(name="updateAll")
async def update_all(ctx):
    with psycopg2.connect(DATABASE_URL) as conn:
        await update_all(conn)


@bot.command()
async def identify(ctx, name: str):
    if not get_color(name):
        await ctx.send("警告：そのようなAtCoderアカウントは見つかりません")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        set_name(name, ctx.author, cur)
        conn.commit()
        print(f"{ctx.author.display_name}'s atcoder_name changed to: {name}")
        if not name.count("`"):
            await ctx.send(f"AtCoderユーザ名が `{name}` に変更されました`")
        else:
            await ctx.send(f"AtCoderユーザ名が変更されました`")
    except Exception as e:
        await ctx.send(f"エラー：{e}")
    finally:
        cur.close()
        conn.close()


async def update_all(conn):
    with conn.cursor() as cur:
        for guild in bot.guilds:
            for member in guild.members:
                if not member.bot:
                    name = get_name(member, cur)
                    conn.commit()
                    color = get_color(name)
                    if color and color != "unrated":
                        await set_role(member, color)


def get_name(member, cur):
    discord_name = f"{member.name}#{member.discriminator}"
    cur.execute("SELECT atcoder_name FROM profile "
                f"WHERE discord_name = '{discord_name}'")
    fetched = cur.fetchone()
    if fetched:
        atcoder_name = fetched[0]
    else:
        atcoder_name = member.display_name
        cur.execute("INSERT INTO profile (discord_name, atcoder_name, color) "
                    f"VALUES ('{discord_name}', '{atcoder_name}', '')")
    return atcoder_name


def set_name(name, member, cur):
    discord_name = f"{member.name}#{member.discriminator}"
    cur.execute("SELECT atcoder_name FROM profile "
                f"WHERE discord_name = '{discord_name}'")
    fetched = cur.fetchone()
    if fetched:
        cur.execute(f"UPDATE profile SET atcoder_name = '{name}' "
                    f"WHERE discord_name = '{discord_name}'")
    else:
        cur.execute("INSERT INTO profile (discord_name, atcoder_name, color) "
                    f"VALUES ('{discord_name}', '{name}', '')")


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