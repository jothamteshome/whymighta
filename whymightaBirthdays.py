import datetime
import disnake

import whymightaDatabase
import whymightaGlobalVariables

from disnake.ext import tasks

# Midnight EST
est = datetime.timezone(-datetime.timedelta(hours=5))
midnight = datetime.time(hour=0, minute=0, tzinfo=est)


@tasks.loop(time=[midnight])
async def birthdayCheck():
    current_date = datetime.datetime.now(tz=est).date()
    user_birthdays = whymightaDatabase.getBirthdayUsers(current_date.month, current_date.day)
    members_to_celebrate = []
    if user_birthdays:
        for user in user_birthdays:
            members_to_celebrate.append(whymightaGlobalVariables.bot.get_user(user['user_id']).mention)

        birthday_embed = disnake.Embed(title=":birthday: Happy Birthday Gamers! :birthday:", color=0x9534eb)
        birthday_embed.add_field(name="-" * 50,
                                 value="\n\n".join([f"{birthday_user}" for birthday_user in members_to_celebrate]))

        birthday_channel = whymightaGlobalVariables.bot.get_channel(
            int(whymightaDatabase.getKey('BIRTHDAY_CHANNEL_KEY')))
        await birthday_channel.send(embed=birthday_embed)


@whymightaGlobalVariables.bot.slash_command(
    description="Add or remove your birthday to receive a message from whymighta!")
async def birthday(inter, add_remove: str, date: str = ""):
    if add_remove.lower() == "add":
        if birthday == "":
            await inter.response.send_message("Please include a birthdate in the form of YYYY-MM-DD")
        else:
            # Check if birthday is a valid date
            if validateBirthday(date):
                formatted_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                whymightaDatabase.addUser(inter.author.id, inter.guild_id)
                whymightaDatabase.addBirthday(inter.author.id, formatted_date)

                await inter.response.send_message(f"{inter.author.mention}, your birthday has been added.")
            else:
                await inter.response.send_message(
                    "There was an error processing that date. Please input a birthdate in the form YYYY-MM-DD")

    elif add_remove.lower() == "remove":
        if not whymightaDatabase.removeBirthday(inter.author.id):
            await inter.response.send_message(f"{inter.author.mention}, your birthday was not in the records. "
                                              f"You can add it now using the `add` subcommand.")
        else:
            await inter.response.send_message(f"{inter.author.mention}, your birthday has been removed.")

    else:
        await inter.response.send_message("Subcommand not available. Please use 'add' or 'remove' only.")


# Validate if a birthday is valid in a calendar year
def validateBirthday(date: str) -> bool:
    birthday_list = date.split("-")
    if len(birthday_list) != 3:
        return False
    else:
        try:
            datetime.date(year=int(birthday_list[0]), month=int(birthday_list[1]), day=int(birthday_list[2]))
        except ValueError:
            return False

    return True
