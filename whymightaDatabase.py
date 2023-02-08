import mysql.connector
import itertools
import whymightaGlobalVariables
import PropertiesReader

from cryptography.fernet import Fernet

prop_reader = PropertiesReader.PropertiesReader()


# Query's the database
# Code from Dr. Ghassemi's CSE 477 course at MSU
def queryDatabase(statement="SELECT * FROM users", parameters=None):
    cnx = mysql.connector.connect(
        host=prop_reader.getDatabaseInfo('MYSQL_HOST'),
        user=prop_reader.getDatabaseInfo('MYSQL_USERNAME'),
        password=prop_reader.getDatabaseInfo('MYSQL_PASSWORD'),
        database=prop_reader.getDatabaseInfo('MYSQL_DATABASE'),
        port=prop_reader.getDatabaseInfo('MYSQL_PORT')
    )

    if parameters is not None:
        cur = cnx.cursor(dictionary=True)
        cur.execute(statement, parameters)
    else:
        cur = cnx.cursor(dictionary=True)
        cur.execute(statement)

    # Fetch one result
    row = cur.fetchall()
    cnx.commit()

    if "INSERT" in statement:
        cur.execute("SELECT LAST_INSERT_ID()")
        row = cur.fetchall()
        cnx.commit()
    cur.close()
    cnx.close()
    return row


# Inserts multiple rows into the database
# Code from Dr. Ghassemi's CSE 477 course at MSU
def insertRows(table, columns, parameters):
    # Check if there are multiple rows present in the parameters
    has_multiple_rows = any(isinstance(el, list) for el in parameters)
    keys, values = ','.join(columns), ','.join(['%s' for x in columns])

    # Construct the query we will execute to insert the row(s)
    statement = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
    if has_multiple_rows:
        for p in parameters:
            statement += f"""({values}),"""
        statement = statement[:-1]
        parameters = list(itertools.chain(*parameters))
    else:
        statement += f"""({values}) """

    insert_id = queryDatabase(statement, parameters)[0]['LAST_INSERT_ID()']
    return insert_id


# Add guild id to 'guilds' table
def addGuild(guild_id):
    whymightaGlobalVariables.guild_ids.append(guild_id)

    insertRows('guilds', ['guild_id'], [guild_id])


# Removes guild id from `guilds` table
def removeGuild(guild_id):
    whymightaGlobalVariables.guild_ids.pop(whymightaGlobalVariables.guild_ids.index(guild_id))

    queryDatabase("DELETE FROM `guilds` WHERE `guild_id` = %s", [guild_id])


# Add encrypted user id and guild id to 'users' table
def addUser(user_id, guild_id):
    insertRows('users', ['user_id', 'guild_id', 'user_chat_score'],
               [[user_id, guild_id, 0]])


# Check a users current chat score
def currentUserScore(user_id, guild_id):
    current_score = queryDatabase("SELECT `user_chat_score` FROM `users` WHERE `user_id` = %s AND `guild_id` = %s",
                                  [user_id, guild_id])[0]['user_chat_score']

    return int(current_score)


# Update's user's server score by amount
def updateUserScore(user_id, guild_id, increased_score):
    queryDatabase("UPDATE `users` SET `user_chat_score` = %s WHERE `user_id` = %s AND `guild_id` = %s",
                  [increased_score, user_id, guild_id])


# Adds encrypted user id and birthday to 'birthdays' table, or updates it if it exists
def addBirthday(user_id, birthday):
    if queryDatabase("SELECT * FROM `birthdays` WHERE `user_id` = %s", [user_id]):
        queryDatabase("DELETE FROM `birthdays` WHERE `user_id` = %s", [user_id])

    insertRows('birthdays', ['user_id', 'birthday'], [[user_id, birthday]])


# Removes a birthday from the 'birthdays'
def removeBirthday(user_id):
    if not queryDatabase("SELECT * FROM `birthdays` WHERE `user_id` = %s", [user_id]):
        return False

    queryDatabase("DELETE FROM `birthdays` WHERE `user_id` = %s", [user_id])
    return True


# Gets all users celebrating their birthday on the current day
def getBirthdayUsers(month, day):
    birthday_users = queryDatabase("SELECT user_id FROM `birthdays` WHERE MONTH(`birthday`) = %s AND DAY(`birthday`) "
                                   "= %s", [month, day])

    return [{'user_id': int(user['user_id'])} for user in birthday_users]


def getKey(identifier):
    encrypted_key = queryDatabase('SELECT `key` FROM `keys` WHERE `key_identifier` = %s', [identifier])[0]['key']
    return reversibleEncrypt('decrypt', encrypted_key)


# Allows for reversible encryption of data
# Code from Dr. Ghassemi's CSE 477 course at MSU
def reversibleEncrypt(method, message):
    fernet = Fernet(prop_reader.getDatabaseInfo('ENCRYPTION_KEY'))

    if method == 'encrypt':
        message = fernet.encrypt(message.encode())
    elif method == 'decrypt':
        message = fernet.decrypt(message).decode()

    return message


# Toggles the mock status of the guild in the database
def toggleMock(guild_id):
    current_status = queryMock(guild_id)

    if current_status:
        queryDatabase("UPDATE `guilds` SET `mock` = %s WHERE `guild_id` = %s", [0, guild_id])
        current_status = False
    else:
        queryDatabase("UPDATE `guilds` SET `mock` = %s WHERE `guild_id` = %s", [1, guild_id])
        current_status = True

    return current_status


# Query's database for mocking status
def queryMock(guild_id):
    current_status = queryDatabase("SELECT `mock` FROM `guilds` WHERE `guild_id` = %s", [guild_id])[0]['mock']

    return current_status
