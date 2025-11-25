import discord
from discord import app_commands
from discord.ext import commands
from database import Database

class ThreadUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.database

        self.upvote_menu = app_commands.ContextMenu(
            name="Upvote",
            callback=self.upvote_message
        )
        self.get_upvotes_menu = app_commands.ContextMenu(
            name="Get Upvotes",
            callback=self.get_upvotes
        )
        self.bot.tree.add_command(self.get_upvotes_menu)
        self.bot.tree.add_command(self.upvote_menu)

    async def upvote_message(self, interaction: discord.Interaction, message: discord.Message):
        if interaction.channel_id != 1440185755745124503:
            await interaction.response.send_message(
                "Upvotes can only be given in the #voting channel.", ephemeral=True
            )
            return

        if message.author.id == interaction.user.id:
            await interaction.response.send_message(
                "You cannot upvote your own message.", ephemeral=True
            )
            return
        
        if message.author.bot:
            await interaction.response.send_message(
                "You cannot upvote bot messages.", ephemeral=True
            )
            return
        
        if len(message.attachments) == 0:
            await interaction.response.send_message(
                "You can only upvote messages with attachments.", ephemeral=True
            )
            return
        
        if await self.db.has_user_upvoted(interaction.user.id, message.id):
            await interaction.response.send_message(
                "You have already upvoted this message.", ephemeral=True
            )
            return
        
        await self.db.log_upvote(interaction.user.id, message.id)
        total_upvotes = await self.db.get_upvotes(message.id)
        await interaction.response.send_message(
            f"You have upvoted this message! It now has {total_upvotes} upvote(s).",
            ephemeral=True
        )

    async def get_upvotes(self, interaction: discord.Interaction, message: discord.Message):
        total_upvotes = await self.db.get_upvotes(message.id)
        await interaction.response.send_message(
            f"This message has {total_upvotes} upvote(s).",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ThreadUtils(bot))
