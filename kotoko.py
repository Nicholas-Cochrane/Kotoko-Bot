import discord
import os
import os.path
import asyncio
import asyncgTTS
import aiohttp
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
    async def wikitext(self, ctx, *, URL):
        text = await wikiparser.wikimediaURLToText(URL)
        await ctx.message.channel.send(text[:2000], reference=ctx.message, mention_author=False)
        
    @commands.command()
    async def wikispeak(self, ctx, *, URL):
        if ctx.voice_client is None:
            return
        
        try:
            nameTuple = wikiparser.wikiURLParse(URL)
        except Exception as e:
            await ctx.message.channel.send("Oops, That URL isn't valid.", reference=ctx.message, mention_author=False)
            raise Exception(e)
            await disconnectFromCTX(ctx)
        
        filePath = "sounds/{}-{}.mp3".format(nameTuple[0],nameTuple[1])
        if(os.path.exists(filePath)):
            await ctx.message.channel.send("Already Created File: Playing \"{}\"".format(nameTuple[1]), reference=ctx.message, mention_author=False)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filePath))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else self.bot.loop.create_task(disconnectFromCTX(ctx)))
            return
        await ctx.message.channel.send("Please way while I parse and generate speech for \"{}\". This may take a few minutes.".format(nameTuple[1]), reference=ctx.message, mention_author=False)
        try:
            text = await wikiparser.wikimediaURLToText(URL)
        except RuntimeError as e:
            await ctx.message.channel.send("Oops, the following error occured: {}".format(e), reference=ctx.message, mention_author=False)
            await disconnectFromCTX(ctx)
        except Exception as e:
            await ctx.message.channel.send("Oops, an error occured parsing the wikipage.", reference=ctx.message, mention_author=False)
            raise Exception(e)
            await disconnectFromCTX(ctx)
            
        try:
            async with aiohttp.ClientSession() as session:
                gtts = await asyncgTTS.setup(premium=False, session=session)
                file_mp3 = await gtts.get(text=text)
                with open(filePath, "wb") as f:
                    f.write(file_mp3)
                #TODO fix time out with long text's
        except OSError as e:
            await ctx.message.channel.send("Oops, an error occured saving the sound file.", reference=ctx.message, mention_author=False)
            raise OSError(e)
            await disconnectFromCTX(ctx)
        except Exception as e:
            await ctx.message.channel.send("Oops, an error occured generating the sound file.", reference=ctx.message, mention_author=False)
            raise Exception(e)
            await disconnectFromCTX(ctx)
        else:
            await ctx.message.channel.send("Finished Creating File: Playing \"{}\"".format(nameTuple[1]), reference=ctx.message, mention_author=False)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filePath))
            ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else self.bot.loop.create_task(disconnectFromCTX(ctx)))
            
        
    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @wikispeak.before_invoke
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


