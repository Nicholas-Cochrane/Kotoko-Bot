import discord
import os
import asyncio
import customwikiparser as wikiparser
from discord.ext import commands

print("Starting Bot...")
#print(os.environ)

TOKEN = os.getenv("discordToken") #put token in system enviroment variables
if TOKEN == None:
    raise Exception("No token was found.")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple test bot')


async def disconnectFromCTX(ctx):
    if not ctx.voice_client.is_playing():
        await ctx.voice_client.disconnect()

async def testAsync():
    print("test")

    
class sound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None

    @commands.command()
    async def test(self, ctx):
        await ctx.send("test")

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, fileName):
        """Plays a file from the local filesystem"""

        if ctx.voice_client is None:
            return
        
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("sounds\\"+fileName))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else self.bot.loop.create_task(disconnectFromCTX(ctx)))
        #https://www.programcreek.com/python/?code=python-discord%2Fseasonalbot%2Fseasonalbot-master%2Fbot%2Fexts%2Fhalloween%2Fspookysound.py

        await ctx.send('Now playing: {}'.format(fileName))
    @commands.command()
    async def wiki(self, ctx, *, URL):
        name = wikiparser.wikiURLParse(URL)
        print(name)

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensureVoice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                #raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


@bot.listen("on_message")
async def response(msg):
    if msg.author == bot.user:
        return
    
    if msg.content.lower() == ('template'):
        responseMsg = 'Response'.format(msg)
        print('template -> response to User:{0.author.name} ID:{0.author.id} in \"{0.guild}\" #{0.channel}'.format(msg))
        await msg.channel.send(responseMsg, reference=msg, mention_author=False)
        
@bot.listen("on_command")
async def beforeCommand(ctx):
    if ctx.message.author == bot.user:
        return
        
    #Log all received messages
    if ctx.message.author != bot.user:
        print("Command:\"{0.content}\" From User:{0.author.name} ID:{0.author.id} in \"{0.guild}\" #{0.channel}".format(ctx.message))
        
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--- Start Log --- \n')

bot.add_cog(sound(bot))
bot.run(TOKEN)


