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

def add_ids(ctx, ids):
    channels_to_append = []
    for id in ids:
        try:
            if get_link(int(id)):
                return f"Channel {id} is already linked elsewhere."
            channel = client.get_channel(int(id))
            if not channel:
                raise ValueError
            channels_to_append.append(channel.id)
        except:
            return f"Channel {id} is invalid."
        
    if len(channels_to_append) < 1:
        return "No channels to link"
    link = get_link(ctx.channel.id)
    if not link:
        config["links"].append({"channels":[ctx.channel.id]})
        save_config(config)
        link = config["links"][-1]

    link["channels"] += channels_to_append
    save_config(config)
    return f"Linked {', '.join(ids)}"
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
async def link(ctx:discord.Message, mode=None, *ids):
    if not mode:
        await ctx.reply("Syntax: `!link add <IDs of channels to link seperated by spaces> | !link clear | !link status`")
    match mode:
        case "clear":
            link = get_link(ctx.channel.id)
            if not link:
                await ctx.reply("This channel isn't connected to a link network.")
                return
            config["links"].remove(link)
            save_config(config)
            await ctx.reply("Cleared link network.")
            return
        case "add":
            if len(ids) < 1:
                await ctx.reply("No IDs specified.")
                return
            await ctx.reply(add_ids(ctx, ids))
        case "status":
            link = get_link(ctx.channel.id)
            if not link:
                await ctx.reply("This channel isn't connected to a link network.")
            await ctx.reply(f"This channel is currently linked to: {', '.join([str(l) for l in link['channels'] if l != ctx.channel.id])}")

def get_link(id):
    for link in config["links"]:
        for channel in link["channels"]:
            if channel == id:
                return link
    return None

@client.event
async def on_message(message:discord.Message):
    if not (
            len(config["links"]) == 0 or
            message.author.bot or
            message.content.startswith(("!","/","."))
        ):
        link = get_link(message.channel.id)
        if link:
            for other_linked_channel in [c for c in link["channels"] if c != message.channel.id]:
                instance = client.get_channel(other_linked_channel)
                await instance.send(message.content)

    await client.process_commands(message)

client.run(config["token"])