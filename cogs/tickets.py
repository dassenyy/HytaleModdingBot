import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import os

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='🎫 Create Ticket', style=discord.ButtonStyle.green, custom_id='create_ticket')
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.id}")
        if existing_channel:
            await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        staff_role = discord.utils.get(guild.roles, name="Staff")
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            f"ticket-{user.id}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Support Ticket",
            description=f"Hello {user.mention}! Thank you for creating a ticket.\nPlease describe your issue and a staff member will assist you shortly.",
            color=discord.Color.green()
        )
        embed.add_field(name="Ticket Owner", value=user.mention, inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(discord.utils.utcnow()), inline=True)

        await channel.send(embed=embed, view=TicketControlView())

        await interaction.response.send_message(f"Ticket created! {channel.mention}", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='🔒 Close Ticket', style=discord.ButtonStyle.red, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔒 Close Ticket",
            description="Are you sure you want to close this ticket?",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=ConfirmCloseView(), ephemeral=True)

class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label='✅ Confirm', style=discord.ButtonStyle.green)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            if not message.author.bot or message.embeds:
                messages.append(f"{message.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {message.author}: {message.content}")

        ticket_owner_id = int(channel.name.split('-')[1])
        ticket_owner = interaction.guild.get_member(ticket_owner_id)
        
        if ticket_owner:
            try:
                transcript_embed = discord.Embed(
                    title="🎫 Ticket Transcript",
                    description=f"Transcript for ticket: {channel.name}",
                    color=discord.Color.blue()
                )
                transcript_content = "\n".join(messages[-20:]) 
                if len(transcript_content) > 1024:
                    transcript_content = transcript_content[-1024:]
                transcript_embed.add_field(name="Recent Messages", value=f"```{transcript_content}```", inline=False)
                
                await ticket_owner.send(embed=transcript_embed)
            except:
                pass

        await interaction.response.send_message("Ticket will be deleted in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        await channel.delete()

    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.red)
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketControlView())
        print("Ticket system loaded!")

    @app_commands.command(name="ticket-panel", description="Create a ticket panel")
    @app_commands.describe(channel="The channel to send the ticket panel to")
    async def ticket_panel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
            return

        target_channel = channel or interaction.channel

        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to create a support ticket.\n\nOur staff team will assist you as soon as possible!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Before creating a ticket:",
            value="• Check FAQ channels\n• Search for existing solutions\n• Be clear about your issue",
            inline=False
        )

        await target_channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message(f"Ticket panel created in {target_channel.mention}!", ephemeral=True)

    @app_commands.command(name="add-user", description="Add a user to the current ticket")
    @app_commands.describe(user="The user to add to the ticket")
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
            return

        ticket_owner_id = int(interaction.channel.name.split('-')[1])
        staff_role = discord.utils.get(interaction.guild.roles, name="Staff")
        
        if interaction.user.id != ticket_owner_id and (not staff_role or staff_role not in interaction.user.roles) and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to add users to this ticket!", ephemeral=True)
            return

        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        
        embed = discord.Embed(
            title="✅ User Added",
            description=f"{user.mention} has been added to this ticket.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-user", description="Remove a user from the current ticket")
    @app_commands.describe(user="The user to remove from the ticket")
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
            return

        ticket_owner_id = int(interaction.channel.name.split('-')[1])
        staff_role = discord.utils.get(interaction.guild.roles, name="Staff")
        
        if interaction.user.id != ticket_owner_id and (not staff_role or staff_role not in interaction.user.roles) and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to remove users from this ticket!", ephemeral=True)
            return

        if user.id == ticket_owner_id:
            await interaction.response.send_message("You cannot remove the ticket owner!", ephemeral=True)
            return

        await interaction.channel.set_permissions(user, overwrite=None)
        
        embed = discord.Embed(
            title="❌ User Removed",
            description=f"{user.mention} has been removed from this ticket.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="close", description="Close the current ticket")
    async def close_ticket_command(self, interaction: discord.Interaction):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
            return

        ticket_owner_id = int(interaction.channel.name.split('-')[1])
        staff_role = discord.utils.get(interaction.guild.roles, name="Staff")
        
        if interaction.user.id != ticket_owner_id and (not staff_role or staff_role not in interaction.user.roles) and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to close this ticket!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 Close Ticket",
            description="Are you sure you want to close this ticket?",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=ConfirmCloseView())

    @app_commands.command(name="ticket-info", description="Get information about the current ticket")
    async def ticket_info(self, interaction: discord.Interaction):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
            return

        ticket_owner_id = int(interaction.channel.name.split('-')[1])
        ticket_owner = interaction.guild.get_member(ticket_owner_id)
        
        embed = discord.Embed(
            title="🎫 Ticket Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Ticket Owner", value=ticket_owner.mention if ticket_owner else "Unknown", inline=True)
        embed.add_field(name="Channel", value=interaction.channel.mention, inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(interaction.channel.created_at), inline=True)
        
        message_count = 0
        async for _ in interaction.channel.history(limit=None):
            message_count += 1
        
        embed.add_field(name="Messages", value=str(message_count), inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tickets(bot))