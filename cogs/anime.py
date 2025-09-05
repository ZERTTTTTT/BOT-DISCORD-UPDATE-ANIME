import os
import json
import asyncio
import requests
import discord
from discord import app_commands, Embed
from discord.ext import commands, tasks
import datetime
from datetime import timezone

TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))
SCHEDULE_SETTINGS_FILE = 'schedule_settings.json'

platform_emojis = {
    'Crunchyroll': '<:crunchyroll:1411884557736743034>',
    'Bilibili':    '<:bilibili:1411885230586986526>',
    'Netflix':     '<:netflix:1411884887450980383>',
    'iQIYI':       '<:iqiyi:1411885698809856140>'
}

def load_settings():
    if os.path.exists(SCHEDULE_SETTINGS_FILE):
        with open(SCHEDULE_SETTINGS_FILE, 'r') as f: return json.load(f)
    return {"isEnabled": True, "time": "08:00"}

def save_settings(settings):
    with open(SCHEDULE_SETTINGS_FILE, 'w') as f: json.dump(settings, f, indent=2)

class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auto_update_task.start()

    async def get_anime_schedule(self, date_string):
        try:
            day, month, year = map(int, date_string.split('-'))
            date_utc = datetime.datetime(year, month, day, 17, 0, 0, tzinfo=timezone.utc)
            airing_at_greater = int(date_utc.timestamp())
            airing_at_lesser = airing_at_greater + (24 * 60 * 60)
            query = """query ($airingAt_greater: Int, $airingAt_lesser: Int) {Page(page: 1, perPage: 50){airingSchedules(airingAt_greater: $airingAt_greater, airingAt_lesser: $airingAt_lesser, sort: TIME){media { title { romaji, english }, genres, isAdult, coverImage { extraLarge }, bannerImage, siteUrl, externalLinks { site, url } }, episode, airingAt}}}"""
            variables = {'airingAt_greater': airing_at_greater, 'airingAt_lesser': airing_at_lesser}
            response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
            data = response.json()
            if not data['data']['Page']['airingSchedules']: return []
            supported_platforms = ['Crunchyroll', 'Bilibili', 'Netflix', 'iQIYI']
            anime_list = []
            for a in data['data']['Page']['airingSchedules']:
                airing_date = datetime.datetime.fromtimestamp(a['airingAt'], tz=datetime.timezone(datetime.timedelta(hours=7)))
                streaming_links = ' • '.join([f'{platform_emojis.get(link["site"], "")} [{link["site"]}]({link["url"]})' for link in a['media']['externalLinks'] if link['site'] in supported_platforms])
                anime_list.append({'title': a['media']['title']['romaji'] or a['media']['title']['english'],'episode': a['episode'],'jadwalLengkap': airing_date.strftime('%A, %d %B %Y\n**Jam:** %H:%M WIB'),'rating': 'Dewasa (18+)' if a['media']['isAdult'] else 'Umum','genres': ', '.join(a['media']['genres'][:3]),'image_url': a['media']['bannerImage'] or a['media']['coverImage']['extraLarge'],'url': a['media']['siteUrl'],'streamingLinks': streaming_links or '_Belum tersedia_'})
            return anime_list
        except Exception as e:
            print(f"API Error: {e}")
            return {'error': 'Gagal mengambil data dari API.'}

    async def send_anime_updates(self, channel, anime_list, date_string):
        header_embed = Embed(color=0x3498db, title=f"📅 Jadwal Rilis Anime - {date_string}", description="Berikut adalah daftar anime yang dijadwalkan tayang hari ini.")
        await channel.send(embed=header_embed)
        if not anime_list:
            await channel.send("😴 Yahh, sepertinya tidak ada jadwal anime baru yang rilis pada tanggal ini.")
            return
        for anime in anime_list:
            embed = Embed(color=0x5865F2, title=anime['title'], url=anime['url'])
            embed.set_image(url=anime['image_url'])
            embed.add_field(name='🗓️ Jadwal Tayang Indonesia', value=anime['jadwalLengkap'], inline=False)
            embed.add_field(name='🎬 Episode', value=f"Episode {anime['episode']}", inline=True)
            embed.add_field(name='🔞 Rating Usia', value=anime['rating'], inline=True)
            embed.add_field(name='📺 Tonton Resmi di', value=anime['streamingLinks'], inline=False)
            embed.add_field(name='🎭 Genre', value=f"_{anime['genres']}_", inline=False)
            embed.set_footer(text="©By ZertScript | Data dari AniList", icon_url='https://i.imgur.com/2d6c2s3.png')
            await channel.send(embed=embed)
            await asyncio.sleep(2)

    @app_commands.command(name="update", description="Kirim jadwal anime manual.")
    async def update(self, interaction: discord.Interaction, tanggal: str = None):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        date_string = tanggal if tanggal else datetime.datetime.now().strftime('%d-%m-%Y')
        anime_list = await self.get_anime_schedule(date_string)
        if isinstance(anime_list, dict) and anime_list.get('error'): await interaction.followup.send(f"❌ Error: {anime_list['error']}")
        else:
            channel = self.bot.get_channel(TARGET_CHANNEL_ID)
            if channel:
                await self.send_anime_updates(channel, anime_list, date_string)
                await interaction.followup.send("✅ Update jadwal selesai dikirim!", ephemeral=True)
            else: await interaction.followup.send("❌ Channel target tidak ditemukan.", ephemeral=True)
    
    @app_commands.command(name="updateautoset", description="Kelola jadwal update anime otomatis.")
    async def updateautoset(self, interaction: discord.Interaction, subcommand: str, waktu: str = None):
        if not interaction.user.guild_permissions.manage_guild: return await interaction.response.send_message("❌ Izin ditolak.", ephemeral=True)
        settings = load_settings()
        if subcommand == 'set':
            if not waktu or not len(waktu.split(':')) == 2 or not all(part.isdigit() for part in waktu.split(':')):
                return await interaction.response.send_message("❌ Format waktu salah! Gunakan `HH:MM`.", ephemeral=True)
            settings['time'] = waktu; settings['isEnabled'] = True
            save_settings(settings); self.auto_update_task.restart()
            return await interaction.response.send_message(f"✅ Jadwal diatur ke jam **{waktu} WIB**.", ephemeral=True)
        elif subcommand == 'on':
            settings['isEnabled'] = True; save_settings(settings)
            if not self.auto_update_task.is_running(): self.auto_update_task.start()
            return await interaction.response.send_message("✅ Jadwal otomatis diaktifkan.", ephemeral=True)
        elif subcommand == 'off':
            settings['isEnabled'] = False; save_settings(settings)
            if self.auto_update_task.is_running(): self.auto_update_task.stop()
            return await interaction.response.send_message("❌ Jadwal otomatis dinonaktifkan.", ephemeral=True)
    
    @tasks.loop(minutes=1)
    async def auto_update_task(self):
        settings = load_settings()
        if not settings.get('isEnabled'): return
        now_wib = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=7)))
        if now_wib.strftime('%H:%M') == settings.get('time', '08:00'):
            print(f"▶️ [AUTO] Menjalankan update jadwal harian...")
            channel = self.bot.get_channel(TARGET_CHANNEL_ID)
            today = now_wib.strftime('%d-%m-%Y')
            anime_list = await self.get_anime_schedule(today)
            if channel and isinstance(anime_list, list):
                await self.send_anime_updates(channel, anime_list, today)
                print("✅ [AUTO] Pengiriman update selesai.")
            else: print("❌ [AUTO] Gagal mengirim update.")
            await asyncio.sleep(61)
    
    @auto_update_task.before_loop
    async def before_auto_update_task(self):
        await self.bot.wait_until_ready()
        print("Mengecek jadwal otomatis anime...")

async def setup(bot: commands.Bot):
    await bot.add_cog(Anime(bot))