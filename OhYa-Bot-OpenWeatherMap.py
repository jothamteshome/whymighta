import PropertiesReader

from discord.ext import commands
from aiohttp import ClientSession

prop_reader = PropertiesReader.PropertiesReader()


class OpenWeatherHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Weather function that takes in a city and unit type and returns the temperature
    @commands.command(name='weather')
    async def weather(self, city="East Lansing", state="", country="", units="imperial"):
        # OpenWeatherMap API key
        weather_api = prop_reader.get('WEATHER_API_KEY')

        # Discord channel key
        channel_key = prop_reader.get('DISCORD_CHANNEL')
        channel = await self.bot.fetch_channel(channel_key)

        # Identifiers for the different temperature units
        temp_identifiers = {'imperial': "\u00B0F", 'metric': "\u00B0C", 'standard': "K"}

        # Weather conditions
        weather_conditions = {'thunderstorm': "It is storming right now.", 'drizzle': "It is drizzling right now",
                              'rain': "It is raining right now.", 'snow': "It is snowing right now.",
                              'clear': "It is clear outside right now.", 'clouds': "It is cloudy right now.",
                              'mist': "It is misty outside right now."}

        # Opens url to OpenWeatherMap API using aiohttp
        async with ClientSession(trust_env=True) as session:

            # Store and process location data from OpenWeatherMap Geocoding API
            async with session.get('https://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},'
                                   '{country_code}&limit={limit}&'
                                   'appid={api_key}'.format(city_name=city, state_code=state, country_code=country,
                                                            limit=1,
                                                            api_key=weather_api)) as loc_response:

                loc_data = await loc_response.json()
                try:
                    lat = loc_data[0]['lat']
                    lon = loc_data[0]['lon']
                    city = loc_data[0]['name'] + ","
                    country = loc_data[0]['country']
                except IndexError:
                    await channel.send("Location not available. Please try again")

                # If state name exists, save it
                # otherwise, save an empty string
                try:
                    state = loc_data[0]['state'] + ","
                except KeyError:
                    state = ""

                # Convert country code to common name
                async with session.get(
                        'https://restcountries.com/v3.1/alpha/{code}'.format(code=country)) as code_response:
                    code_data = await code_response.json()
                    country = code_data[0]['name']['common']

                async with session.get(
                        "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
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
                    await channel.send(
                        "The temperature in {city} {state} {country} right now is {current:.2f}{temp_id}, "
                        "with a high of {high:.2f}{temp_id} and a low of {low:.2f}{temp_id}. "
                        "{condition}".format(city=city, state=state, country=country,
                                             current=current_temp, high=high_temp, low=low_temp,
                                             temp_id=temp_identifiers[units.lower()],
                                             condition=current_condition))
                # If KeyError exception because invalid unit, send valid types to Discord server
                except KeyError:
                    await channel.send("Invalid unit type. Valid unit types are standard, metric, or imperial.")

    @commands.command(name='weather_message')
    async def weather_message(self, message):
        check_help = False
        channel = message.channel
        valid_units = ['imperial', 'metric', 'standard']
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "weather", "")
        user_message = user_message.split()

        # Remove any hyphens from locations
        for i in range(0, len(user_message)):
            if "-" in user_message[i]:
                user_message[i] = user_message[i].replace("-", " ")

        # Try to use all user-inputted data points, and if they do not
        # exist, try to use less until just the default function call is sent
        if len(user_message) == 4:
            if user_message[3].lower() in valid_units:
                await self.weather(user_message[0], user_message[1], user_message[2].lower(), user_message[3])
            else:
                check_help = True
        elif len(user_message) == 3:
            if user_message[2].lower() in valid_units:
                await self.weather(user_message[0], user_message[1], '', user_message[2].lower())
            else:
                await self.weather(user_message[0], user_message[1], user_message[2])
        elif len(user_message) == 2:
            if user_message[1].lower() in valid_units:
                await self.weather(user_message[0], '', '', user_message[1].lower())
            else:
                await self.weather(user_message[0], '', user_message[1])
        elif len(user_message) == 1:
            await self.weather(user_message[0])
        elif len(user_message) == 0:
            await self.weather()
        else:
            check_help = True

        if check_help:
            await channel.send("Please check j!help for proper use of this function")


def setup(bot):
    bot.add_cog(OpenWeatherHandler(bot))
