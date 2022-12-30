import disnake
import PropertiesReader
import signal

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


class TheListHandler:
    def __init__(self, bot):
        self.bot = bot

    # Add a name to the list
    async def list_add(self, person, channel):
        names[person] = None
        await channel.send("Added {person} to the list!".format(person=person))

    # Remove a name from the list
    async def list_remove(self, person, channel):
        try:
            names.pop(person)
            await channel.send("Removed {person} from the list!".format(person=person))
        except KeyError:
            await channel.send("{person} is not on the list.".format(person=person))

    # Display the list
    async def list_show(self, channel):
        embed = disnake.Embed(title="The List", color=0x9534eb)
        formatted_line = ""
        for name in names:
            formatted_line += "`" + name + "`\n "
        embed.description = formatted_line
        await channel.send(embed=embed)

    async def on_list_message(self, message):
        check_help = False
        # Receive parameters from message
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "the_list", "")
        user_message = user_message.split()

        # If message has 2 parameters check whether
        # to add or remove from the list
        if len(user_message) == 2:

            # Before adding to the list, confirm message author is
            # allowed to add to the list, then add to the list
            if user_message[0].lower() == "add":
                if message.author.id == prop_reader.get_user('NAME_ONE_ID'):
                    await self.list_add(user_message[1].title(), message.channel)
                else:
                    user = await self.bot.fetch_user(prop_reader.get_user('NAME_ONE_ID'))
                    await message.channel.send('Only {user} can access this command'
                                               .format(user=user))

            # Before removing from the list, confirm message author
            # is allowed to remove from the list, then remove from the list
            elif user_message[0].lower() == "remove":
                if message.author.id == prop_reader.get_user('NAME_ONE_ID'):
                    await self.list_remove(user_message[1].title(), message.channel)
                else:
                    user = await self.bot.fetch_user(prop_reader.get_user('NAME_ONE_ID'))
                    await message.channel.send('Only {user} can access this command'
                                               .format(user=user))
            else:
                check_help = True

        # If message has 1 parameter, check if it
        # is to view the list
        elif len(user_message) == 1:
            if user_message[0].lower() == "view":
                await self.list_show(message.channel)
            else:
                check_help = True

        # If no parameter in message, also view the list
        elif len(user_message) == 0:
            await self.list_show(message.channel)
        else:
            check_help = True

        if check_help:
            await message.channel.send("Please check j!help for proper use of this function")