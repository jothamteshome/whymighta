import disnake
import time


class Utilities:
    def __init__(self, bot):
        self.bot = bot

    async def ping(self, message):
        before = time.monotonic()
        embed = disnake.Embed(title=":information_source: | Pong!", description="\n", color=0x9534eb)
        message = await message.channel.send(embed=embed)
        latency = (time.monotonic() - before) * 1000
        embed.add_field(name="Latency", value=str(int(latency)) + "ms", inline=False)
        embed.add_field(name="API", value=str(int(self.bot.latency * 1000)) + "ms", inline=False)
        await message.edit(embed=embed)

    async def clear(self, channel, number=5):
        # Add one to account for the calling message
        await channel.purge(limit=number + 1)

    async def utilities_message(self, message):
        if self.bot.command_prefix + "ping" in message.content:
            await self.ping(message)
        elif self.bot.command_prefix + "clear" in message.content:
            user_message = message.content
            user_message.replace(self.bot.command_prefix + "clear", "")
            user_message = user_message.split()

            # Only allow command if message author is an administrator to prevent trolling
            if message.author.guild_permissions.administrator:
                try:
                    # If user input a valid number, use inputted parameter,
                    # otherwise use a default 5
                    if str(user_message[1]).isnumeric():
                        if int(user_message[1]) < 1 or int(user_message[1]) > 100:
                            await message.channel.send("Cannot perform operation. Please select a number of posts "
                                                       "between 1 and 100")
                        else:
                            await self.clear(message.channel, int(user_message[1]))
                except IndexError:
                    await self.clear(message.channel)
            else:
                await message.channel.send(
                    "This command is only available to Server Administrators. Contact an administrator "
                    "for assistance.")
