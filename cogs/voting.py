import discord
from discord import app_commands
from discord.ext import commands, tasks

import asyncio
from database import Database

class Voting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.database

        self.upvote_menu = app_commands.ContextMenu(
            name="Upvote",
            callback=self.upvote_message
        )
        self.bot.tree.add_command(self.upvote_menu)
        self.update_votes.start()

    def cog_unload(self):
        self.update_votes.cancel()
        return super().cog_unload()

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
            upvotes = await self.db.get_upvotes(message.id)
            await interaction.response.send_message(
                f"You have already upvoted this message. This message has {upvotes} upvote(s).", ephemeral=True
            )
            return
        
        await self.db.log_upvote(interaction.user.id, message.id)
        total_upvotes = await self.db.get_upvotes(message.id)
        await interaction.response.send_message(
            f"You have upvoted this message! It now has {total_upvotes} upvote(s).",
            ephemeral=True
        )

    @tasks.loop(seconds=30)
    async def update_votes(self):
        showcases = await self.db.get_top_5_showcases()
        channel = self.bot.get_channel(1440185755745124503)
        if not isinstance(channel, discord.TextChannel):
            return

        messages = await channel.history(limit=100).flatten()
        if len(messages) < 5: 
            for _ in range(5 - len(messages)):
                await channel.send("Showcase placeholder message.")
        for message in messages:
            if message.author.bot:
                continue
            upvotes = await self.db.get_upvotes(message.id)
            
            embed = discord.Embed(
                title="Community Showcase",
                description=message.content if message.content else "No description provided",
                color=discord.Color.blue(),
                timestamp=message.created_at
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url
            )
            embed.add_field(
                name="Upvotes",
                value=f"⬆️ {upvotes}",
                inline=True
            )
            
            if message.attachments:
                attachment = message.attachments[0]
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    embed.set_image(url=attachment.url)
                else:
                    embed.add_field(
                        name="Attachment",
                        value=f"[{attachment.filename}]({attachment.url})",
                        inline=False
                    )
            
            embed.add_field(
                name="Original Message",
                value=f"[Jump to Message]({message.jump_url})",
                inline=True
            )

            await message.edit(content=message.author.mention, embed=embed)


async def setup(bot):
    await bot.add_cog(Voting(bot))
