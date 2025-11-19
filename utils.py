import discord
from discord import ButtonStyle

import datetime
import time
import yaml

class TicketStaffPing(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ping Staff", custom_id="ticket:ping", style=ButtonStyle.primary)
    async def ping_staff(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        message = [message async for message in interaction.channel.history(limit=1, oldest_first=True)][0]

        embed = message.embeds[0]
        owner = int(embed.fields[0].value.replace("<@", "").replace(">", ""))

        if interaction.user.id != owner:
            return await interaction.followup.send("You are not the creator of this ticket!", ephemeral=True)
        
        bot = interaction.client
        staff_role: discord.Role = bot.support_staff

        msg = await interaction.channel.send(staff_role.mention)
        await msg.delete()

        button.disabled = True
        await interaction.edit_original_response(view=self)

class TicketTypeSelect(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=None)
        self.selected = None
        self.user = user
        
        # Load product roles from config
        config = get_server_config("plugin")
        product_roles = config.get("product_roles", [])
        
        options = []
        
        # Add product-specific options if user has the role
        for product in product_roles:
            role = discord.utils.get(user.roles, id=product["role_id"])
            if role:
                options.append(discord.SelectOption(
                    label=product["label"],
                    description=product["description"],
                    value=product["value"]
                ))
        
        # Always add general options
        options.append(discord.SelectOption(
            label="General Support",
            description="General questions and support",
            value="general"
        ))
        
        options.append(discord.SelectOption(
            label="Purchase Issue",
            description="Issues with purchasing or accessing a product",
            value="purchase"
        ))

        select = discord.ui.Select(
            placeholder="Select ticket type",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_type_select"
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This isn't your ticket!", ephemeral=True)
            return False
        return True

    async def select_callback(self, interaction: discord.Interaction):
        self.selected = interaction.data["values"][0]
        await interaction.response.defer()
        self.stop()

class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create ticket", style=ButtonStyle.primary, emoji="🎫", custom_id="ticket:create")
    async def create_ticket_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        bot = interaction.client

        await interaction.response.defer(ephemeral=True)

        category = bot.support_category
        staff_role = bot.support_staff

        # Create ticket channel immediately
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
        }

        channel: discord.TextChannel = await category.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )

        success_e = discord.Embed(
            description=f"Your ticket has been created: {channel.mention}\n\nPlease follow the steps to complete your ticket setup.",
            timestamp=datetime.datetime.now(),
            color=discord.Color.nitro_pink()
        )
        success_e.set_author(name="Ticket created")
        success_e.set_footer(text=bot.version, icon_url=bot.icon)
        await interaction.followup.send(embed=success_e, ephemeral=True)

        # Step 1: Ask for BuiltByBit username
        creation_1 = discord.Embed(
            description="Welcome to your support ticket!\n\nPlease enter your **BuiltByBit username** below. This helps us verify your purchases and provide better support.",
            color=discord.Color.nitro_pink(),
            timestamp=datetime.datetime.now()
        )
        creation_1.set_author(name="Ticket Setup (Step 1/2)")
        creation_1.set_footer(text=bot.version, icon_url=bot.icon)
        
        msg = await channel.send(interaction.user.mention, embed=creation_1)

        def bbb_check(m):
            return m.author.id == interaction.user.id and m.channel.id == channel.id

        try:
            bbb_msg = await bot.wait_for("message", timeout=300, check=bbb_check)
            bbb_username = bbb_msg.content
            await bbb_msg.delete()
        except:
            timeout_e = discord.Embed(
                description="Ticket creation timed out. This channel will be deleted.",
                color=discord.Color.red()
            )
            timeout_e.set_footer(text=bot.version, icon_url=bot.icon)
            await channel.send(embed=timeout_e)
            await channel.delete(delay=5)
            return

        # Step 2: Select ticket type
        creation_2 = discord.Embed(
            description=f"Thank you, **{bbb_username}**!\n\nNow, please select the type of support you need from the dropdown below.",
            color=discord.Color.nitro_pink(),
            timestamp=datetime.datetime.now()
        )
        creation_2.set_author(name="Ticket Setup (Step 2/2)")
        creation_2.set_footer(text=bot.version, icon_url=bot.icon)
        
        select_view = TicketTypeSelect(interaction.user)
        await msg.edit(embed=creation_2, view=select_view)
        await select_view.wait()

        if not select_view.selected:
            timeout_e = discord.Embed(
                description="Ticket creation timed out. This channel will be deleted.",
                color=discord.Color.red()
            )
            timeout_e.set_footer(text=bot.version, icon_url=bot.icon)
            await channel.send(embed=timeout_e)
            await channel.delete(delay=5)
            return

        # Finalize ticket
        ticket_type_labels = {
            "novastaff": "NovaStaff Support",
            "castlesiege": "CastleSiege Support",
            "general": "General Support",
            "purchase": "Purchase Issue"
        }

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)
        }
        
        await channel.edit(
            topic=f"{ticket_type_labels.get(select_view.selected, 'Support')} ticket created by {interaction.user.mention} - <t:{round(time.time())}:R>",
            overwrites=overwrites
        )

        channel_e = discord.Embed(
            description="Your ticket has been set up successfully! A support team member will assist you shortly.\n\nPlease provide as much detail as possible about your issue while you wait.",
            timestamp=datetime.datetime.now(),
            color=discord.Color.nitro_pink()
        )
        channel_e.set_author(name="Ticket Information")
        channel_e.add_field(name="Creator", value=f"{interaction.user.mention}", inline=True)
        channel_e.add_field(name="BuiltByBit Username", value=f"`{bbb_username}`", inline=True)
        channel_e.add_field(name="Ticket Type", value=f"{ticket_type_labels.get(select_view.selected, 'Support')}", inline=True)
        channel_e.set_footer(text=bot.version, icon_url=bot.icon)
        
        await msg.delete()
        await channel.send(embed=channel_e)
        
        # Ping staff silently
        ping_msg = await channel.send(staff_role.mention)
        await ping_msg.delete()

def load_configuration():
    with open("config.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def get_server_config(server: str):
    with open(f"server-configs/{server}.yml", "r") as f:
        server_config = yaml.load(f, Loader=yaml.FullLoader)
    return server_config