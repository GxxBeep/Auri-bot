from discord.ext import commands
from discord import app_commands
import discord

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("VoiceChat cog loaded")

    @app_commands.command(name="join", description="Entra em um canal de voz.")
    async def join(self, interaction: discord.Interaction):
        await interaction.response.send_message(" Entrando no canal de voz...")

async def setup(bot):
    await bot.add_cog(Test(bot))