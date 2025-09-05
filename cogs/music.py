import discord
from discord import app_commands, Embed, FFmpegPCMAudio
from discord.ext import commands
import yt_dlp

YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True', 'quiet': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music_players = {}

    @app_commands.command(name="play", description="Memutar musik dari YouTube.")
    async def play(self, interaction: discord.Interaction, judul_atau_url: str):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        if not interaction.user.voice: return await interaction.response.send_message("Kamu harus berada di voice channel!", ephemeral=True)
        
        await interaction.response.defer()
        
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try: info = ydl.extract_info(f"ytsearch:{judul_atau_url}", download=False)['entries'][0]
            except Exception: return await interaction.followup.send("❌ Tidak dapat menemukan lagu tersebut.")

        url = info['url']
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(interaction.user.voice.channel)
        else:
            voice_client = await interaction.user.voice.channel.connect()

        voice_client.play(FFmpegPCMAudio(url, **FFMPEG_OPTIONS))
        self.music_players[interaction.guild.id] = voice_client
        
        embed = Embed(title="🎵 Now Playing", description=f"[{info['title']}]({info['webpage_url']})", color=0xff0000)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stop", description="Menghentikan musik dan keluar dari voice channel.")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        if interaction.guild.id in self.music_players:
            voice_client = self.music_players[interaction.guild.id]
            if voice_client.is_playing(): voice_client.stop()
            await voice_client.disconnect()
            del self.music_players[interaction.guild.id]
            await interaction.response.send_message("Musik dihentikan dan bot keluar.")
        else:
            await interaction.response.send_message("Bot tidak sedang memutar musik.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))