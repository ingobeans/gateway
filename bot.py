import discord, random, os, json
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

if not os.path.isfile("config.json"):
    with open("config.json","w") as f:
        json.dump(
        {
            "token":None,
            "links":[]
        }, f, indent=4)

def load_config():
    with open("config.json","r") as f:
        return json.load(f)

def save_config(config):
    with open("config.json","w") as f:
        json.dump(config, f, indent=4)

config = load_config()

if not config["token"]:
    print("You need to configure a token in config.json")
    quit()

@client.event
async def on_ready():
    print("Bot is ready!")
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game("with beans"))

@client.command()
async def cmd(ctx):
    await ctx.send("This is a command 🤠, " + ctx.author.name)

def get_link(id):
    for link in config["links"]:
        for channel in link["channels"]:
            if channel == id:
                return link
    return None

@client.event
async def on_message(message:discord.Message):
    if config["links"] and not message.author.bot:
        link = get_link(message.channel.id)
        if link:
            for other_linked_channel in [c for c in link["channels"] if c != message.channel.id]:
                instance = client.get_channel(other_linked_channel)
                await instance.send(message.content)

    await client.process_commands(message)

client.run(config["token"])