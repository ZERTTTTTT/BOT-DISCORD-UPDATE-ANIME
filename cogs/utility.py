import psutil
import discord
from discord import app_commands, Embed
from discord.ext import commands
import datetime
from datetime import timezone

start_time = datetime.datetime.now(timezone.utc)

def format_uptime(duration):
    days, r = divmod(duration.total_seconds(), 86400)
    hours, r = divmod(r, 3600)
    minutes, _ = divmod(r, 60)
    return f"{int(days)} hari, {int(hours)} jam, {int(minutes)} menit"

class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Mengetes koneksi bot.")
    async def ping(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(embed=Embed(title="Pong! 🏓", description=f"API Latency: `{latency}ms`", color=0x3498db))

    @app_commands.command(name="info", description="Menampilkan informasi tentang bot.")
    async def info(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        embed = Embed(title="Informasi Bot", description="Bot jadwal anime dan musik.", color=0x2ecc71)
        embed.add_field(name="Pembuat", value="©By ZertScript", inline=True).add_field(name="Library", value="discord.py", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info-panel", description="Melihat status CPU, RAM, dan uptime bot.")
    async def info_panel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        cpu = psutil.cpu_percent(1); ram = psutil.virtual_memory()
        embed = Embed(title="📊 Panel Informasi Bot", color=0x2ecc71)
        embed.add_field(name="CPU Usage", value=f"`{cpu}%`", inline=True)
        embed.add_field(name="RAM Usage", value=f"`{ram.used/(1024**3):.2f} GB / {ram.total/(1024**3):.2f} GB ({ram.percent}%)`", inline=False)
        embed.add_field(name="Ping", value=f"`{round(self.bot.latency*1000)}ms`", inline=True)
        embed.add_field(name="Waktu Berjalan", value=f"`{format_uptime(datetime.datetime.now(timezone.utc) - start_time)}`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="nuke", description="Membersihkan channel ini.")
    async def nuke_channel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        await interaction.response.send_message("💥 Membersihkan channel...", ephemeral=True)
        new_channel = await interaction.channel.clone(reason="Nuked")
        await interaction.channel.delete()
        await new_channel.send(f"✅ Channel berhasil dibersihkan oleh {interaction.user.mention}!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))