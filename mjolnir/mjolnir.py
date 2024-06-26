import asyncio
import logging
import random
import typing
from contextlib import suppress

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify
from . import menus  # Ensure this is a relative import for the Mjolnir class
log = logging.getLogger(__name__)

sayings = (
    "The hammer is strong, but so are you. Keep at it!",
    "Mjolnir budges a bit, but remains steadfast, as should you",
    "You've got this! I believe in you!",
    "Don't think it even moved... why don't you try again?",
)


class Mjolnir(commands.Cog):
    """Attempt to lift Thor's hammer!"""

    __version__ = "0.1.1"
    __author__ = ["Jojo", "Kreusada"]

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, 1242351245243535476356, True)
        self.config.register_user(lifted=0)

    async def red_delete_data_for_user(self, *, requester, user_id: int):
        await self.config.user_from_id(user_id).clear()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad"""
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    @commands.command()
    async def lifted(self, ctx: commands.Context):
        """Shows how many times you've lifted the hammer."""
        lifted = await self.config.user(ctx.author).lifted()
        plural = "s" if lifted != 1 else ""
        await ctx.send(f"You have lifted Mjolnir {lifted} time{plural}.")

    @commands.cooldown(1, 60.0, commands.BucketType.user)
    @commands.command()
    async def trylift(self, ctx: commands.Context):
        """Try and lift Thor's hammer!"""
        lifted = random.randint(0, 100)
        if lifted >= 95:
            await ctx.send(
                "The sky opens up and a bolt of lightning strikes the ground\nYou are worthy. Hail, son of Odin."
            )
            return await self.config.user(ctx.author).lifted.set(
                (await self.config.user(ctx.author).lifted()) + 1
            )
        await ctx.send(random.choice(sayings))

    @commands.command()
    async def liftedboard(self, ctx: commands.Context):
        """Shows the leaderboard for those who have lifted the hammer."""
        from mjolnir import menus  # Import here to avoid circular import
        
        all_users = await self.config.all_users()
        board = sorted(all_users.items(), key=lambda m: m[1]["lifted"], reverse=True)
        sending = []
        for user in board:
            _user = await self.bot.get_or_fetch_user(user[0])
            name = _user.display_name
            amount = user[1]["lifted"]
            sending.append(f"**{name}:** {amount}")
        sending = list(pagify("\n".join(sending)))
        if not len(sending):
            msg = f"No one has lifted Mjolnir yet!\nWill you be the first? Try `{ctx.clean_prefix}trylift`"
            if await ctx.embed_requested():
                embed = discord.Embed(
                    title="Mjolnir!",
                    description=msg,
                    colour=discord.Colour.blue(),
                )
                return await ctx.send(embed=embed)
            return await ctx.send(msg)
        await menus.MjolnirMenu(source=menus.MjolnirPages(sending)).start(
            ctx=ctx, channel=ctx.channel
        )

    async def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            with suppress(discord.Forbidden):
                await ctx.send("Sorry, this is only for guilds!")
            return False
        return True

async def setup(bot: Red):
    await bot.add_cog(Mjolnir(bot))
