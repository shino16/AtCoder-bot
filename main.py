import discord
from urllib.request import urlopen
from bs4 import BeautifulSoup


TOKEN = 'Njg1MTU0MjM0OTE5OTQ0MjE5.XmGhAQ.LA46-0Gdo4bEa_v3ttwDLRQP6-g'

client = discord.Client()


@client.event
async def on_ready():
    try:
        for guild in client.guilds:
            for member in guild.members:
                if not member.bot:
                    color = get_color(member.display_name)
                    if color:
                        await set_role(member, color)
    finally:
        await client.logout()


def get_color(name):
    try:
        html = urlopen("https://atcoder.jp/users/" + name)
        soup = BeautifulSoup(html, "html.parser")
        span_tag = soup.find("a", class_="username").find("span")
        style = span_tag.get("class")[0]
        return style[5:] if style != "user-unrated" else None
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


client.run(TOKEN)