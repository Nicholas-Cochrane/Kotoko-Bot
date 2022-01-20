import discord
import os
import asyncio
from discord.ext import commands

print("Starting Bot...")
#print(os.environ)

TOKEN = os.getenv("discordToken") #put token in system enviroment variables
if TOKEN == None:
    raise Exception("No token was found.")


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
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        if ctx.voice_client is None:
            return
        
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else self.bot.loop.create_task(disconnectFromCTX(ctx)))
        #https://www.programcreek.com/python/?code=python-discord%2Fseasonalbot%2Fseasonalbot-master%2Fbot%2Fexts%2Fhalloween%2Fspookysound.py

        await ctx.send('Now playing: {}'.format(query))


    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                #raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


   
"""@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
        
    #Log all received messages
    if message.author != bot.user:
        print("Received Message: {0.content}".format(message))
        print("From: {0.author.id} \n".format(message))
        
    #Test 
    if message.content.lower() == ('template'):
        msg = 'Response {0.author.mention}'.format(message)
        print('Sending:')
        print(msg + '\n')
        await message.channel.send(msg)
        
		
    if message.content.lower() == 'test':
       voicestate = message.author.voice
       print(voicestate.channel.name)
       VoiceProtocol = await voicestate.channel.connect()
       audio = await discord.FFmpegOpusAudio.from_probe("monsterkill.mp3")
       VoiceProtocol.play(audio, after= lambda e: print("played audio", e))"""

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple test bot')
        
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--- Start Log ---')

bot.add_cog(sound(bot))
bot.run(TOKEN)
