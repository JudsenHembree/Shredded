import discord
import asyncio
import pathlib

async def blast(interaction: discord.Interaction):
    user = interaction.user
    voice_channel = user.voice.channel
    if voice_channel != None:
        #check for blast
        if not pathlib.Path('interject/audio_clips/blast.mp3').exists():
            await interaction.followup.send('Blast audio not found', ephemeral=True)
            return
        await interaction.followup.send('BLASTIN', ephemeral=True)
        source = None
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('interject/audio_clips/blast.mp3'))
        except Exception as e:
            print('Error loading audio')
            print(e)
        if source is not None:
            try:
                voice_client = await voice_channel.connect()
                voice_client.play(source, )
                while voice_client.is_playing():
                    await asyncio.sleep(1)
                await voice_client.disconnect()
            except Exception as e:
                print('Error playing audio')
                print(e)

async def blast_macro(bot: discord.Bot):
    user = bot.get_all_members()
    voice_channel = None
    for member in user:
        if member.id == 293100675133341699:
            voice_channel = member.voice.channel
    if voice_channel == None:
        print('User not in voice channel')
        return
    #check for blast
    if not pathlib.Path('interject/audio_clips/blast.mp3').exists():
        print('Blast audio not found')
        return
    source = None
    try:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('interject/audio_clips/blast.mp3'))
    except Exception as e:
        print('Error loading audio')
        print(e)
    if source is not None:
        try:
            voice_client = await voice_channel.connect()
            voice_client.play(source, )
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()
        except Exception as e:
            print('Error playing audio')
            print(e)
