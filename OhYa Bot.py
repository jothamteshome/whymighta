import discord
import PropertiesReader
import praw

from aiohttp import ClientSession
from datetime import date

# Initialize reader for properties file
prop_reader = PropertiesReader.PropertiesReader()

# Load bot token from a file
TOKEN = prop_reader.get('DISCORD_TOKEN')

prefix = 'j!'

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.typing = True

# Instantiate a Discord client
discordClient = discord.Client(intents=intents)

# Get the date on start-up
today = date.today()


@discordClient.event
async def on_ready():
    print("Logged in as {0.user}".format(discordClient))
    await on_reddit()


# Weather function that takes in a city and unit type and returns the temperature
@discordClient.event
async def weather(city="East Lansing", state="", country="", units="imperial"):
    # OpenWeatherMap API key
    weather_api = prop_reader.get('WEATHER_API_KEY')

    # Discord channel key
    channel_key = prop_reader.get('DISCORD_CHANNEL')
    channel = await discordClient.fetch_channel(channel_key)

    # Identifiers for the different temperature units
    temp_identifiers = {'imperial': "\u00B0F", 'metric': "\u00B0C", 'standard': "K"}

    # Weather conditions
    weather_conditions = {'thunderstorm': "It is storming right now.", 'drizzle': "It is drizzling right now",
                          'rain': "It is raining right now.", 'snow': "It is snowing right now.",
                          'clear': "It is clear outside right now.", 'clouds': "It is cloudy right now."}

    # Opens url to OpenWeatherMap API using aiohttp
    async with ClientSession(trust_env=True) as session:

        # Store and process location data from OpenWeatherMap Geocoding API
        async with session.get('https://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},'
                               '{country_code}&limit={limit}&'
                               'appid={api_key}'.format(city_name=city, state_code=state, country_code=country, limit=1,
                                                        api_key=weather_api)) as loc_response:

            loc_data = await loc_response.json()
            lat = loc_data[0]['lat']
            lon = loc_data[0]['lon']
            city = loc_data[0]['name'] + ","
            country = loc_data[0]['country']

            # If state name exists, save it
            # otherwise, save an empty string
            try:
                state = loc_data[0]['state'] + ","
            except KeyError:
                state = ""

            # Convert country code to common name
            async with session.get('https://restcountries.com/v3.1/alpha/{code}'.format(code=country)) as code_response:
                code_data = await code_response.json()
                country = code_data[0]['name']['common']

            async with session.get("https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
                                   "&units={unit_type}".format(lat=lat, lon=lon, api_key=weather_api,
                                                               unit_type=units)) as weather_response:

                # Store and process weather data from OpenWeatherMap API
                try:
                    weather_data = await weather_response.json()
                    current_temp = weather_data['main']['temp']
                    high_temp = weather_data['main']['temp_max']
                    low_temp = weather_data['main']['temp_min']
                    current_condition = weather_conditions[weather_data['weather'][0]['main'].lower()]
                except KeyError:
                    await channel.send("Invalid entry. Please check spelling and try again.")

            # Try to send weather information to Discord server
            try:
                await channel.send("The temperature in {city} {state} {country} right now is {current:.2f}{temp_id}, "
                                   "with a high of {high:.2f}{temp_id} and a low of {low:.2f}{temp_id}. "
                                   "{condition}".format(city=city, state=state, country=country,
                                                        current=current_temp, high=high_temp, low=low_temp,
                                                        temp_id=temp_identifiers[units.lower()],
                                                        condition=current_condition))
            # If KeyError exception because invalid unit, send valid types to Discord server
            except KeyError:
                await channel.send("Invalid unit type. Valid unit types are standard, metric, or imperial.")


@discordClient.event
async def on_reddit():
    user = prop_reader.get('REDDIT_USERNAME')
    password = prop_reader.get('REDDIT_PASSWORD')
    app_id = prop_reader.get('REDDIT_APP_ID')
    secret = prop_reader.get('REDDIT_APP_SECRET')
    user_agent = 'OhYa Bot by u/' + user
    reddit = praw.Reddit(client_id=app_id, client_secret=secret,
                         user_agent=user_agent, username=user, password=password)

    reddit.read_only = True


@discordClient.event
async def on_message(message):
    channel = message.channel
    if message.author.bot is not True:
        if message.content == prefix:
            await channel.send("Did you mean to use a function?\n Current functions: weather")
        if prefix + "help" in message.content:
            await channel.send("*Weather :* j!weather [City-Name] [State-Code*(optional)*] "
                               "[Country-Code*(optional)*] [Units-Type]")
        elif prefix + "weather" in message.content:
            user_message = message.content
            user_message = user_message.replace(prefix + "weather ", "")
            user_message = user_message.split()

            # Remove any hyphens from locations
            for i in range(0, len(user_message)):
                if "-" in user_message[i]:
                    user_message[i].replace("-", " ")

            # Try to use all user-inputted data points, and if they do not
            # exist, try to use less until just the default function call is sent
            try:
                await weather(user_message[0], user_message[1], user_message[2], user_message[3])
            except IndexError:
                try:
                    await weather(user_message[0], "", user_message[1], user_message[2])
                except IndexError:
                    try:
                        await weather(user_message[0], "", "", user_message[1])
                    except IndexError:
                        if user_message[0] not in ['imperial', 'metric', 'standard']:
                            try:
                                await weather(user_message[0])
                            except IndexError:
                                await weather()
                        else:
                            await weather()


discordClient.run(TOKEN)
