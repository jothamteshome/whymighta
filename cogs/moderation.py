import logging

import disnake
from disnake.ext import commands

logger = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(
        description="Clear up to 100 messages from the current channel at once",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def purge(self, inter: disnake.ApplicationCommandInteraction, number: int = 5) -> None:
        if number < 1 or number > 100:
            await inter.response.send_message("Number must be between 1 and 100.")
            return
        message_str = "message" if number == 1 else "messages"
        logger.info(
            "Purge: %d messages in channel %d (guild %d) by user %d",
            number,
            inter.channel.id,
            inter.guild.id,
            inter.author.id,
        )
        await inter.response.send_message(f"{inter.author} cleared {number} {message_str} from the channel")
        await inter.channel.purge(limit=number + 1)


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Moderation(bot))
