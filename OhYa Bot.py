import discord
import PropertiesReader
import requests
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
    # await weather()
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
async def on_reddit(subreddit='itswiggles_', sort_by='hot', top_sort=''):
    # Load reddit credentials
    user = prop_reader.get('REDDIT_USERNAME')
    password = prop_reader.get('REDDIT_PASSWORD')
    app_id = prop_reader.get('REDDIT_APP_ID')
    secret = prop_reader.get('REDDIT_APP_SECRET')

    # Discord channel key
    channel_key = prop_reader.get('DISCORD_CHANNEL')
    channel = await discordClient.fetch_channel(channel_key)

    # Login with credentials
    auth = requests.auth.HTTPBasicAuth(app_id, secret)
    data = {'grant_type': 'password', 'username': user, 'password': password}

    headers = {'user-agent': 'OhYa Bot by ' + user}

    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    reddit_token = res.json()['access_token']
    headers['Authorization'] = 'bearer {}'.format(reddit_token)

    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    api = 'https://oauth.reddit.com'
    reddit = 'https://reddit.com'

    res = requests.get('{}/r/{subreddit}/{sort_by}{top_sort}'.format(api, subreddit=subreddit, sort_by=sort_by,
                                                                     top_sort=top_sort), headers=headers,
                       params={'limit': 5})

    sub_res = requests.get('{}/r/{subreddit}/about'.format(api, subreddit=subreddit))

    user_res = requests.get('{}/u/TheRealFroJoe'.format(api))

    # print(sub_res.json())
    # sub_description = sub_res_data['data']['public_description']
    # if sub_res_data['data']['community_icon']:
    #    subreddit_icon = sub_res_data['data']['community_icon']
    # else:
    #    subreddit_icon = sub_res_data['data']['icon_img']

    posts = []

    # Store data from 5 reddit posts
    for post in res.json()['data']['children']:
        post_data = {}
        post_data['author'] = post['data']['author']
        post_data['title'] = post['data']['title']
        post_data['selftext'] = post['data']['selftext']
        if post['data']['media_embed']:
            url = post['data']['media_embed']['content']
            url = url.split("src=\"")[1]
            url = url.split("\"")[0]
            post_data['media_embed'] = url
        else:
            post_data['media_embed'] = ""
        post_data['upvotes'] = int(post['data']['ups'])
        post_data['downvotes'] = int(post['data']['ups']) - int(
            int(post['data']['ups'] * float(post['data']['upvote_ratio'])))

        posts.append(post_data)

    embed = discord.Embed(title="Top 5 Posts of All Time", color=0xFF5733)
    embed.set_author(name="r/" + subreddit, url='{}/r/{subreddit}/{sort_by}{top_sort}'
                     .format(reddit, subreddit=subreddit, sort_by=sort_by, top_sort=top_sort),
                     icon_url='https://external-preview.redd.it/QJRqGgkUjhGSdu3vfpckrvg1UKzZOqX2BbglcLhjS70.png'
                              '?auto=webp&s=c681ae9c9b5021d81b6c4e3a2830f09eff2368b5')
    embed.add_field(name='\u200b', value='-' * 95)

    for i in range(1, 6):
        if not posts[i]['selftext'] and posts[i]['media_embed']:
            embed.add_field(name=posts[i]['title'], value=posts[i]['media_embed'], inline=False)
        elif posts[i]['selftext']:
            embed.add_field(name=posts[i]['title'], value=posts[i]['selftext'], inline=False)
        embed.add_field(name="Upvotes", value=str(posts[i]['upvotes']), inline=True)
        embed.add_field(name="Downvotes", value=str(posts[i]['downvotes']), inline=True)
        if i < 5:
            embed.add_field(name="u/" + posts[i]['author'], value='-' * 95, inline=False)
    embed.add_field(name="u/" + posts[i]['author'], value='-' * 95, inline=False)

    await channel.send(embed=embed)


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
            user_message = user_message.replace(prefix + "weather", "")
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
                        if user_message[0].lower() not in ['imperial', 'metric', 'standard']:
                            try:
                                await weather(user_message[0])
                            except IndexError:
                                await weather()
                        else:
                            await weather()

        elif prefix + "reddit" in message.content:
            valid_sort_types = ['hot', 'new', 'top', 'rising']
            valid_top_sorts = {'now': '/?t=hour', 'day': '/?t=day', 'week': '/?t=week',
                               'month': '/?t=month', 'year': "/?t=year", 'all': '/?t=all'}
            user_message = message.content
            user_message = user_message.replace(prefix + "reddit", "")
            user_message = user_message.split()
            try:
                if user_message[1].lower() not in valid_sort_types:
                    await channel.send(
                        "Not a valid sorting condition\nValid conditions are: Hot | New | Top | Rising")
                elif user_message[1].lower() != 'top':
                    await on_reddit(user_message[0], user_message[1])
                elif user_message[1].lower() == 'top' and user_message[2].lower() not in valid_top_sorts:
                    await channel.send("Not a valid sorting condition for 'Top' posts\n"
                                       "Valid conditions are: Now | Day | Week | Month | Year | All")
                else:
                    await on_reddit(user_message[0], user_message[1], valid_top_sorts[user_message[2]])
            except IndexError:
                try:
                    if user_message[0] not in valid_top_sorts or user_message[0] not in valid_sort_types:
                        await on_reddit(user_message[0])
                except IndexError:
                    await on_reddit()


discordClient.run(TOKEN)
