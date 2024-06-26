import json
import pathlib

from redbot.core.bot import Red

# Ensure correct import paths
from .mjolnir import Mjolnir
from . import menus  # Ensure this is a relative import

# Load the end user data statement
with open(pathlib.Path(__file__).parent / "info.json") as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]

async def setup(bot: Red):
    bot.add_cog(Mjolnir(bot))
