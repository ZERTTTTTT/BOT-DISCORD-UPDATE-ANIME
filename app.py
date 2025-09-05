import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Cog '{filename}' berhasil dimuat.")
                except Exception as e:
                    print(f"❌ Gagal memuat cog '{filename}': {e}")
        
        try:
            synced = await self.tree.sync()
            print(f"✅ Sinkronisasi {len(synced)} slash commands.")
        except Exception as e:
            print(f"❌ Gagal sinkronisasi commands: {e}")

    async def on_ready(self):
        print(f'🤖 Bot {self.user} sudah online!')
        await self.change_presence(activity=discord.Game(name="Jadwal Anime & Musik"))

bot = MyBot()
bot.run(TOKEN)