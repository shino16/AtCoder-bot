import discord

token = 'Njg1MTU0MjM0OTE5OTQ0MjE5.XmEjVA.pbsz8FPjk3kZ5siqgz43noL2fLM'

client = discord.Client()

@client.event
async def on_ready():
    print('Ready!')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    print("Received: " + message.content)

client.run(token)
