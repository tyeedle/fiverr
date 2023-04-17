import discord
import ffmpeg
import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
import nextcord.ui
import os
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from gtts import gTTS
import dotenv
import os

dotenv.load_dotenv()

bot = commands.Bot(command_prefix="ta!",intents=nextcord.Intents.all(),activity=nextcord.Activity(name=f"Pycharm",type=nextcord.ActivityType.watching))


logsID = 1094663991214751864
TOKEN = str(os.environ.get("TOKEN"))
print(TOKEN)
fiverrLink = "https://www.fiverr.com/sweetpotatoe236/create-a-high-quality-custom-bot"
url = "https://www.google.com/search?q={}"
guild_ids = [1077562765033615381]

class Menu(nextcord.ui.View):
    def __init__(self):
        super().__init__(

        )
        self.value = None


class FeedbackModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Send us your feedback",timeout=120)

        self.fb_title = nextcord.ui.TextInput(
            style=nextcord.TextInputStyle.short,
            label="Title",
            max_length=128,
            min_length=2,
            required=False,
            placeholder="Give your feedback a title"
        )

        self.message = nextcord.ui.TextInput(
            style=nextcord.TextInputStyle.paragraph,
            label="Message",
            max_length=256,
            min_length=4,
            required=False,
            placeholder="Type your message here"
        )
        self.add_item(self.fb_title)
        self.add_item(self.message)

    async def callback(self, interaction : nextcord.Interaction):
        channel = interaction.guild.get_channel(1094746192723845192)
        embed = nextcord.Embed(title=f"New Feedback - {self.fb_title.value}",
                                  description=f"```{self.message.value}```",
                                  color=nextcord.Colour.from_rgb(128,128,128))
        embed.set_author(name=interaction.user.name)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you, {interaction.user.name} for your feedback!",ephemeral=True)

    async def on_error(self,error,interaction:nextcord.Interaction):
        await interaction.response.send_message("Sorry , there was an error with your feedback",ephemeral=True)

    async def on_timeout(self):
        self.stop()


@tasks.loop(seconds=3, )
async def assitance():
    server = bot.get_guild(1077562765033615381)
    logs_channel = bot.get_channel(logsID)
    for channel in server.channels:

        if isinstance(channel, nextcord.TextChannel):
            if channel.name.startswith("closed-"):
                messages = [message async for message in channel.history(limit=100)]
                messages = reversed(messages)
                with open("transcript.txt", "a") as f:
                    for message in messages:
                        if "Ticket Tool" in str(message.author):
                            continue
                        f.write(f"\n{message.author} -> {message.content}\n")

                await channel.delete()
                break

    await logs_channel.send(f"```Transcript of ticket```",
                            file=nextcord.File(r"C:\Users\tyren\PycharmProjects\fiverr\transcript.txt"))
    os.remove(r"C:\Users\tyren\PycharmProjects\fiverr\transcript.txt")

@bot.slash_command(name="tts",description="Make Ticket Assistant Say Something (Must Be In VC)")
async def tts(interaction:discord.Interaction,message:str):

    user = interaction.user
    if user.voice:
        try:

            vc = await user.voice.channel.connect()
        except Exception as err:
            vc = interaction.guild.voice_client
        sound = gTTS(text=message,lang="en",slow=False)
        sound.save("tts-audio.mp3")
        if vc.is_playing():
            await interaction.guild.voice_client.disconnect(force=True)
        source = await nextcord.FFmpegOpusAudio.from_probe("tts-audio.mp3", method="fallback")
        vc.play(source)

        await interaction.response.send_message("Success",ephemeral=True,delete_after=5)
    else:
        await interaction.response.send_message("You Must Be In A VC To Do This")

@bot.slash_command(name="disconnect",description="Kicks bot from any vc channel")
async def disconnect(interaction:discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("Disconnected Bot Successfully",ephemeral=True,delete_after=5)
    else:
        await interaction.response.send_message("Bot is not in vc",ephemeral=True,delete_after=5)

@bot.slash_command(name="fiverr",description="Direct Link To My Product on Fiverr",guild_ids=guild_ids)
async def fiverr(interaction:nextcord.Interaction):
    view=Menu()
    view.add_item(nextcord.ui.Button(label="Link To Fiverr Page",style=nextcord.ButtonStyle.link,url=fiverrLink))
    await interaction.response.send_message(view=view,ephemeral=True)


@bot.slash_command(name="help",description="Displays A List Of All Working Commands",guild_ids=guild_ids)
async def help(interaction:nextcord.Interaction):
    await interaction.response.send_message(embed=nextcord.Embed(title="All Working Commands",description=">>> " +"\n".join([f"**/{command.name}** - {command.description}" for command in bot.get_all_application_commands()])),ephemeral=True)


@bot.slash_command(name="softban",description="Instantly Bans And Unbans A User, Clearing All Their Chats",guild_ids=guild_ids)
async def softban(interaction:nextcord.Interaction,user:nextcord.User):
    guild = nextcord.utils.get(bot.guilds,id=1077562765033615381)
    await guild.ban(user)
    await guild.unban(user)
    await interaction.response.send_message(f"Successfully soft banned {user.mention}")


@bot.slash_command(name="unbanall",description="Unbans Every Banned User On The Server",guild_ids=guild_ids)
async def unbanall(interaction:nextcord.Interaction):
    bans = interaction.guild.bans()
    unbanned = []
    for ban_entry in bans:
        unbanned.append(ban_entry.user)
        await interaction.guild.unban(ban_entry.user)
    await interaction.response.send_message(f"Banned {len(unbanned)} Users." + "\n".join([user.name for user in unbanned]))


@bot.slash_command(name="google", description="Searches google and gives you the first result", guild_ids=guild_ids)
async def google(interaction:nextcord.Interaction,query:str):
    urls = []
    for i in search(query,num_results=5):
        urls.append(i)
    await interaction.response.send_message("```Here Are 5 Websites That Relate To Your Search!```"+ "\n".join(urls),ephemeral=True,suppress_embeds=True)




@bot.slash_command(name="feedback", description="Send feedback to us directly via nextcord!", guild_ids=guild_ids)
async def feedback(interaction:nextcord.Interaction):
    feedback_modal = FeedbackModal()
    feedback_modal.user = interaction.user
    await interaction.response.send_modal(modal=feedback_modal)

@bot.slash_command(name="userinfo",description="Gets A Users Information And Presents It As An Embed")
async def userinfo(interaction:nextcord.Interaction,user:nextcord.Member):
    embed = nextcord.Embed(title=f"{user.name}'s Info",colour=nextcord.Colour.from_rgb(100,100,255))
    embed.set_author(name=user.name,icon_url=user.avatar.url)

    args = {
        "avatar" : user.avatar.url,
        "is_bot" : user.bot,
        "created_at" : user.created_at.strftime("%b %d, %Y, %T"),
        "joined_at" : user.created_at.strftime("%b %d, %Y, %T"),
        "server": interaction.guild,
        "top role" : user.top_role,
        "nick" : user.nick,
        "status" : user.status,

    }
    if user.activity:
        args["activity"] = f"{user.activity.name}"

    for (argk,argv) in args.items():
        embed.add_field(name=f"{argk}:",value=argv,inline=True)
    embed.set_footer(text=f"id: {user.id}")
    embed.set_thumbnail(user.display_avatar)
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.slash_command(name="mimic",description="?")
async def mimic(interaction:discord.Interaction,user:discord.User,message:str):
    webhook = await interaction.channel.create_webhook(name=user.name)
    await webhook.send(message,username=user.name,avatar_url=user.avatar.url)
    webhooks = await interaction.channel.webhooks()
    for webhook in webhooks:
        await webhook.delete()
    await interaction.response.send_message(content="Completed",delete_after=0.1,ephemeral=True)


@bot.event
async def on_ready():
    print(f"{bot.user.name} {bot.activity.url} {bot.activity.name}")
    await assitance.start()




bot.run(TOKEN)

