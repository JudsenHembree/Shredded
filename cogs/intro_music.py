"""
Allow users to play a 7 second clip of a song.
When they join voice chat, the bot will play the song.
"""

from subprocess import run, CalledProcessError, PIPE
import asyncio
import os
from glob import glob
from os import path
from discord import (
        Option, 
        ApplicationContext, 
        File, 
        FFmpegPCMAudio,
        Member,
        VoiceState,
        VoiceChannel
        )
from discord.ext import commands
from discord.commands import SlashCommandGroup

class IntroMusic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_playing = False

    Music_Manager = SlashCommandGroup(name="music", 
                                      description="Handle intro music \
                                              related commands.")

    async def play_intro(self, member: Member, channel: VoiceChannel):
        print("playing intro music for " + str(member) + " in " + str(channel) + "!")

        if self.is_playing:
            return
        if not member.voice:
            return
        if channel is None:
            return
        dir = "intro_music/" + str(member)
        if not path.exists(dir):
            return
        if len(glob(dir + "/*.wav")) == 0:
            return

        # load the song
        song_download = glob(dir + "/*.wav")[0]

        # have mike join the voice channel
        voice_client = await channel.connect()
        voice_client.play(FFmpegPCMAudio(song_download))
        self.is_playing = True
        while voice_client.is_playing():
            await asyncio.sleep(0.5)
        self.is_playing = False
        await voice_client.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member , before: VoiceState, 
                                    after: VoiceState):
        """on channel join, play intro music"""
        if member.bot:
            return
        if before.channel is not after.channel and after.channel is not None:
            await self.play_intro(member, after.channel)

    @Music_Manager.command(name='select_intro', 
                           description="Provide a Spotify URL for the song",
                           options=[Option(input_type=str, name="url", 
                           description="Must be a Spotify URL and \
                                   Not a playlist", required=True),
                                    Option(input_type=int, name="start_time",
                                           description="Start time in seconds"),
                                    Option(input_type=int, name="duration",
                                           description="Duration in seconds < 10")])
    async def select_intro(self, ctx: ApplicationContext, url: str, start_time: int,
                           duration: int = 7 ):
        await ctx.defer()

        if int(duration) > 10:
            await ctx.followup.send("Duration must be less than 10 seconds!")
            return

        duration_str = str(duration)
        user = ctx.author
        dir = "/tmp/music/" + str(user)
        if start_time is None:
            start_time = 0

        if not path.exists(dir):
            os.makedirs(dir)
        else:
            for f in glob(dir + "/*"):
                os.remove(f)

        proc = await asyncio.create_subprocess_shell("spotdl " + url,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE,
                                                     cwd=dir)
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            await ctx.followup.send("Error during download: " + stderr.decode())
            return

        song_download = glob(dir + "/*.mp3")[0]
        proc = await asyncio.create_subprocess_shell("ffmpeg -ss " + str(start_time) +
                                                     " -i \"" + song_download + "\" -t " 
                                                     + duration_str + " -f wav \""
                                                     + song_download + "_clip.wav\"",
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)

        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            await ctx.followup.send("Error during clipping: " + stderr.decode())
            return

        # copy to local directory
        if not path.exists("intro_music/" + str(user)):
            os.makedirs("intro_music/" + str(user))
        else:
            for f in glob("intro_music/" + str(user) + "/*"):
                os.remove(f)

        proc = await asyncio.create_subprocess_shell("cp \"" + song_download + 
                                                     "_clip.wav\" intro_music/" + str(user)
                                                     )
                    
        await ctx.followup.send("Intro music selected! Use /music play to play it.",
                                ephemeral=True,
                                file=File(song_download + "_clip.wav"))

    @Music_Manager.command(name='play', 
                           description="Play your intro music.")
    async def play(self, ctx: ApplicationContext):
        await ctx.defer()
        if self.is_playing:
            await ctx.followup.send("Mike is already playing music! Wait your turn.")
            return
        user = ctx.author
        if not ctx.author.voice:
            await ctx.followup.send("You must be in a voice channel to play intro music!")
            return
        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.followup.send("You must be in a voice channel to play intro music!")
            return
        dir = "intro_music/" + str(user)
        if not path.exists(dir):
            await ctx.followup.send("You haven't selected any intro music yet! \
                              Use /music select_intro to select some.")
            return
        if len(glob(dir + "/*.wav")) == 0:
            await ctx.followup.send("You haven't selected any intro music yet! \
                              Use /music select_intro to select some.")
            return

        # check if mike is already playing Music
        if self.is_playing:
            await ctx.followup.send("Mike is already playing music! Wait your turn.")
            return

        # load the song
        song_download = glob(dir + "/*.wav")[0]

        # have mike join the voice channel
        await channel.connect()
        await ctx.followup.send("Playing intro music!", ephemeral=True)
        ctx.voice_client.play(FFmpegPCMAudio(song_download))
        self.is_playing = True
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)
        self.is_playing = False
        await ctx.voice_client.disconnect()


def setup(bot):
    bot.add_cog(IntroMusic(bot))
