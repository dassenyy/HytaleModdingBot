import discord
from discord.ext import commands

class Keywords(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    async def get_replied_message(self, ctx: commands.Context) -> discord.Message:
        if ctx.message.reference:
            replied_message = ctx.message.reference.resolved
            if replied_message is None:
                replied_message = await ctx.channel.fetch_message(
                    ctx.message.reference.message_id
                )
        else:
            replied_message = ctx.message
        return replied_message

    @commands.command()
    async def languages(self, ctx: commands.Context):
        replied_message = await self.get_replied_message(ctx)
        
        e = discord.Embed(description="Hytale will support the following languages:\n\n- Server Side (Plugins): Java\n- Client Side (Modding): C#\n\n-# *This information is subject to change as Hytale is still in development. It is not confirmed.*")
        e.set_footer(text="Hytale Modding", icon_url='https://img.willofsteel.me/u/p2SdbC.png')
        await replied_message.reply(embed=e)
    
    @commands.command()
    async def security(self, ctx: commands.Context):
        replied_message = await self.get_replied_message(ctx)
        
        e = discord.Embed(description="Hypixel Studios have a bug bounty program to help improve the security of Hytale. \n\n### [Click here or the link above to visit](https://hytale.com/security)")
        e.set_footer(text="Hytale Modding", icon_url='https://img.willofsteel.me/u/p2SdbC.png')
        await replied_message.reply(content="https://hytale.com/security", embed=e)

    @commands.command()
    async def site(self, ctx: commands.Context):
        replied_message = await self.get_replied_message(ctx)
        
        await replied_message.reply("https://github.com/HytaleModding/site")

    @commands.command()
    async def bot(self, ctx: commands.Context):
        replied_message = await self.get_replied_message(ctx)
        
        await replied_message.reply("https://github.com/HytaleModding/robot")

async def setup(bot):
    await bot.add_cog(Keywords(bot))