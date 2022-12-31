import datetime
import disnake
import whymightaGlobalVariables
import PropertiesReader

from disnake.ext import tasks

# Initialize reader for properties file
prop_reader = PropertiesReader.PropertiesReader()

# Midnight EST
est = datetime.timezone(-datetime.timedelta(hours=5))
midnight = datetime.time(hour=0, minute=0, tzinfo=est)

@tasks.loop(time=[midnight])
async def birthdayCheck():
    current_date = datetime.datetime.now(tz=est).date()
    date_key = f"{current_date.month}-{current_date.day}"
    birthdays = whymightaGlobalVariables.birthdate_user.get(date_key)
    birthday_users = []
    if birthdays is not None:
        for user_id in birthdays:
            birthday_users.append(whymightaGlobalVariables.bot.get_user(user_id).mention)

        birthday_embed = disnake.Embed(title=":birthday: Happy Birthday Gamers! :birthday:", color=0x9534eb)
        birthday_embed.add_field(name="-" * 50, value="\n\n".join([f"{birthday_user}" for birthday_user in birthday_users]))

        birthday_channel = whymightaGlobalVariables.bot.get_channel(int(prop_reader.get_key('BIRTHDAY_CHANNEL_KEY')))
        await birthday_channel.send(embed=birthday_embed)

@whymightaGlobalVariables.bot.slash_command(
    description="Add or remove your birthday to receive a message from whymighta!",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def birthday(inter, subcommand: str, date: str = ""):
    if subcommand.lower() == "add":
        if birthday == "":
            await inter.response.send_message("Please include a birthdate in the form of YYYY-MM-DD")
        else:
            # Check if birthday is a valid date
            if validateBirthday(date):
                formatted_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

                # Check if birthday-->user connection exists
                if formatted_date in whymightaGlobalVariables.birthdate_user:
                    whymightaGlobalVariables.birthdate_user[f"{formatted_date.month}-{formatted_date.day}"].append(inter.author.id)
                else:
                    whymightaGlobalVariables.birthdate_user[f"{formatted_date.month}-{formatted_date.day}"] = [inter.author.id]

                # If user id is already stored, update it in both dictionaries
                if inter.author.id in whymightaGlobalVariables.user_birthdate:
                    existing_date = whymightaGlobalVariables.user_birthdate[inter.author.id]
                    whymightaGlobalVariables.birthdate_user[existing_date].remove(inter.author.id)

                    # Remove date if list is empty
                    if len(whymightaGlobalVariables.birthdate_user[existing_date]) == 0:
                        whymightaGlobalVariables.birthdate_user.pop(existing_date)

                # Add user-->birthday connection for easier lookup when removing
                whymightaGlobalVariables.user_birthdate[inter.author.id] = f"{formatted_date.month}-{formatted_date.day}"
                await inter.response.send_message(f"{inter.author.mention}, your birthday has been added.")
            else:
                await inter.response.send_message("There was an error processing that date. Please input a birthdate in the form YYYY-MM-DD")


    elif subcommand.lower() == "remove":
        if inter.author.id not in whymightaGlobalVariables.user_birthdate:
            await inter.response.send_message(f"{inter.author.mention}, your birthday was not in the records. "
                                              f"You can add it now using the `add` subcommand.")
        else:
            date = whymightaGlobalVariables.user_birthdate.pop(inter.author.mention, None)

            # If date exists in birthday-->user connections, remove user id from birthday list
            if date is not None:
                whymightaGlobalVariables.birthdate_user[date].remove(inter.author.id)

                # Remove date if list is empty
                if len(whymightaGlobalVariables.birthdate_user[date]) == 0:
                    whymightaGlobalVariables.birthdate_user.pop(date)

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

# Save birthdays to file every hour
@tasks.loop(hours=1)
async def saveBirthdays():
    file = prop_reader.open('BIRTHDAYS', 'w')
    for date in whymightaGlobalVariables.birthdate_user:
        user_ids = "; ".join([str(user_id) for user_id in whymightaGlobalVariables.birthdate_user[date]])
        file.write(f"{date}, {user_ids}\n")
    file.close()

    whymightaGlobalVariables.birthdate_user = {}
    whymightaGlobalVariables.user_birthdate = {}
    loadBirthdays()

# Load birthdays to dictionary from file
def loadBirthdays():
    file = prop_reader.open('BIRTHDAYS', 'r')
    for date in file:
        user_birthday = date.replace('\n', "").split(', ')
        user_ids = user_birthday[1].split("; ")

        user_ids = [int(user_id) for user_id in user_ids]

        whymightaGlobalVariables.birthdate_user[user_birthday[0]] = user_ids

        for user_id in user_ids:
            whymightaGlobalVariables.user_birthdate[user_id] = user_birthday[0]

    file.close()
