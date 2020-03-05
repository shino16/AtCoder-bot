import discord
import os
import psycopg2
from urllib.request import urlopen
from bs4 import BeautifulSoup


TOKEN = 'Njg1MTU0MjM0OTE5OTQ0MjE5.XmEjVA.pbsz8FPjk3kZ5siqgz43noL2fLM'

DATABASE_URL = os.environ['DATABASE_URL']

client = discord.Client()


@client.event
async def on_ready():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        for guild in client.guilds:
            for member in guild.members:
                if not member.bot:
                    update_color(member, cur)
                    await set_role(member, cur)
    finally:
        conn.close()
        cur.close()
        await client.logout()


def update_color(member, cur):
    discord_name = f"{member.name}#{member.discriminator}"
    cur.execute("SELECT atcoder_name FROM profile "
                f"WHERE discord_name = '{discord_name}'")
    fetched = cur.fetchone()
    if fetched is None:
        atcoder_name = member.display_name
        cur.execute("INSERT INTO profile (discord_name, atcoder_name, color) "
                    f"VALUES ('{discord_name}', '{atcoder_name}', '')")
    else:
        atcoder_name = fetched[0]
    color = get_color(atcoder_name)
    if color:
        print(f"Updating {atcoder_name}'s color to {color}")
        cur.execute(f"UPDATE profile SET color = '{color}' "
                    f"WHERE discord_name = '{discord_name}'")


def get_color(name):
    try:
        html = urlopen("https://atcoder.jp/users/" + name)
        soup = BeautifulSoup(html, "html.parser")
        span_tag = soup.find("a", class_="username").find("span")
        style = span_tag.get("class")[0]
        return style[5:] if style != "user-unrated" else None
    except:
        print(f"An error occured while handling '{name}'")
        return None


async def set_role(member, cur):
    print(f"Setting the role of {member.name}#{member.discriminator}")
    cur.execute("SELECT color FROM profile WHERE discord_name = "
                f"'{member.name}#{member.discriminator}'")
    record = cur.fetchone()
    if not record:
        return
    color = record[0]
    roles = [role for role in member.guild.roles
             if role.name.startswith(color)]
    if roles:
        try:
            await member.edit(roles=roles)
            print("Set: " + ", ".join(role.name for role in roles))
        except discord.errors.Forbidden:
            print("Permission denied")
    else:
        print("[Bug] Role not found")


client.run(TOKEN)