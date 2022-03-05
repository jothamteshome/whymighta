import disnake
import PropertiesReader
import signal


from disnake.ext import commands

prop_reader = PropertiesReader.PropertiesReader()

# Read in the names from file and store them in dictionary
names = {}
file = prop_reader.open("THE_LIST", 'r')
for line in file:
    line = line.replace("\n", "")
    names[line] = None
file.close()


# On SIGINT, write all current names to file
def signal_handler(sig, frame):
    file = prop_reader.open("THE_LIST", "w")
    for name in names:
        file.write(name + "\n")
    file.close()


signal.signal(signal.SIGINT, signal_handler)


class TheListHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def list_add(self, person, channel):
        names[person] = None
        await channel.send("Added {person} to the list!".format(person=person))

    async def list_remove(self, person, channel):
        try:
            names.pop(person)
            await channel.send("Removed {person} from the list!".format(person=person))
        except KeyError:
            await channel.send("{person} is not on the list.".format(person=person))

    async def list_show(self, channel):
        embed = disnake.Embed(title="The List", color=0x9534eb)
        formatted_line = ""
        for name in names:
            formatted_line += "`" + name + "`\n "
        embed.description = formatted_line
        await channel.send(embed=embed)

    @commands.command(name='on_list_message')
    async def on_list_message(self, message):
        check_help = False
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "the_list", "")
        user_message = user_message.split()
        if len(user_message) == 2:
            if user_message[0] == "add":
                if message.author == prop_reader.get_name('NAME_ONE'):
                    await self.list_add(user_message[1].title(), message.channel)
                else:
                    await message.channel.send('Only {user} can access this command'
                                               .format(user=prop_reader.get_name('NAME_ONE')))
            elif user_message[0] == "remove":
                if message.author == prop_reader.get_name('NAME_ONE'):
                    await self.list_remove(user_message[1].title(), message.channel)
                else:
                    await message.channel.send('Only {user} can access this command'
                                               .format(user=prop_reader.get_name('NAME_ONE')))
            else:
                check_help = True
        elif len(user_message) == 1:
            if user_message[0] == "add":
                check_help = True
            elif user_message[0] == "view":
                await self.list_show(message.channel)
        elif len(user_message) == 0:
            await self.list_show(message.channel)
        else:
            check_help = True

        if check_help:
            await message.channel.send("Please check j!help for proper use of this function")


def setup(bot):
    bot.add_cog(TheListHandler(bot))