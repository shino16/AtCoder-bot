import discord
import os
import psycopg2


TOKEN = 'Njg1MTU0MjM0OTE5OTQ0MjE5.XmEjVA.pbsz8FPjk3kZ5siqgz43noL2fLM'

DATABASE_URL = os.environ['DATABASE_URL']

client = discord.Client()


@client.event
async def on_ready():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for guild in client.guilds:
                for member in guild.members:
                    if not member.bot:
                        update_color(member, cur)
                        await set_role(member, cur)
    await client.logout()

def update_color(member, cur):
    color = "blue"
    cur.execute("SELECT COUNT(*) FROM profile WHERE discord_name = "
                f"'{member.name}#{member.discriminator}'")
    count = cur.fetchone()
    if count:
        cur.execute(f"UPDATE profile SET color = '{color}' WHERE discord_name = "
                    f"'{member.name}#{member.discriminator}'")
    else:
        cur.execute("INSERT INTO profile (discord_name, atcoder_name, color)"
                    "VALUES ('{member.name}#{member.discriminator}'"
                    "        '{member.name}', '{color}')")

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
        await member.edit(roles=roles)
        print("Set: " + ", ".join(role.name for role in roles))
    else:
        print("[Warning] Role not found")


client.run(TOKEN)
