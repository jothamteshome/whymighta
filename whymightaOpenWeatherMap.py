import whymightaGlobalVariables

from aiohttp import ClientSession


@whymightaGlobalVariables.bot.slash_command(
    description="Check the weather in a specific city",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def weather(inter, units: str, city: str, state_code: str = "", country_code: str = ""):
    valid_units = {"F": 'imperial', "C": 'metric', "K": 'standard'}

    if units.upper() in valid_units:
        units = valid_units[units.upper()]
        # OpenWeatherMap API key
        weather_api = whymightaGlobalVariables.prop_reader.get_key('WEATHER_API_KEY')

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
                                   'appid={api_key}'.format(city_name=city, state_code=state_code, country_code=country_code,
                                                            limit=1,
                                                            api_key=weather_api)) as loc_response:

                loc_data = await loc_response.json()
                try:
                    lat = loc_data[0]['lat']
                    lon = loc_data[0]['lon']
                    city = loc_data[0]['name'] + ","
                    country_code = loc_data[0]['country']
                except IndexError:
                    await inter.response.send_message("Location not available. Please try again")

                # If state name exists, save it
                # otherwise, save an empty string
                try:
                    state = loc_data[0]['state'] + ","
                except KeyError:
                    state = ""

                # Convert country code to common name
                async with session.get(
                        'https://restcountries.com/v3.1/alpha/{code}'.format(code=country_code)) as code_response:
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
                        await inter.response.send_message("Invalid entry. Please check spelling and try again.")

                # Try to send weather information to Discord server
                try:
                    await inter.response.send_message(
                        "The temperature in {city} {state} {country} right now is {current:.2f}{temp_id}, "
                        "with a high of {high:.2f}{temp_id} and a low of {low:.2f}{temp_id}. "
                        "{condition}".format(city=city, state=state, country=country,
                                             current=current_temp, high=high_temp, low=low_temp,
                                             temp_id=temp_identifiers[units.lower()],
                                             condition=current_condition))
                # If KeyError exception because invalid unit, send valid types to Discord server
                except KeyError:
                    await inter.response.send_message("Invalid unit type. Valid unit types are standard, metric, or imperial.")

    else:
        await inter.response.send_message("Invalid unit type. Valid unit types are standard, metric, or imperial.")

