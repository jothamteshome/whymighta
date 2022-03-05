from disnake.ext import commands


class ClearHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clear')
    async def clear(self, channel, number=5):
        # Add one to account for the calling message
        await channel.purge(limit=number+1)

    @commands.command(name='on_clear_message')
    async def on_clear_message(self, message):
        channel = message.channel
        user_message = message.content
        user_message.replace(self.bot.command_prefix + "clear", "")
        user_message = user_message.split()

        # Only allow command if message author is an administrator to prevent trolling
        if message.author.guild_permissions.administrator:
            try:
                if str(user_message[1]).isnumeric():
                    if int(user_message[1]) < 1 or int(user_message[1]) > 100:
                        await channel.send("Cannot perform operation. Please select a number of posts "
                                           "between 1 and 100")
                    else:
                        await self.clear(channel, int(user_message[1]))
            except IndexError:
                await self.clear(channel)
        else:
            await channel.send("This command is only available to Server Administrators. Contact an administrator "
                               "for assistance.")


def setup(bot):
    bot.add_cog(ClearHandler(bot))
