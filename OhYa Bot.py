import discord
import PropertiesReader
import asyncpraw
import asyncprawcore

from aiohttp import ClientSession
from datetime import datetime

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
today = datetime.now()


@discordClient.event
async def on_ready():
    print("Logged in as {0.user}".format(discordClient))


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
                          'clear': "It is clear outside right now.", 'clouds': "It is cloudy right now.",
                          'mist': "It is misty outside right now."}

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
async def on_reddit(sub='itswiggles_', sort_by='hot', top_sort='', num_posts=5):

    # Get Discord channel
    channel_id = prop_reader.get('DISCORD_CHANNEL')
    channel = await discordClient.fetch_channel(channel_id)

    # Login to Reddit with asyncpraw
    user = prop_reader.get('REDDIT_USERNAME')
    password = prop_reader.get('REDDIT_PASSWORD')
    app_id = prop_reader.get('REDDIT_APP_ID')
    secret = prop_reader.get('REDDIT_APP_SECRET')
    user_agent = 'OhYa Bot by u/' + user
    reddit = asyncpraw.Reddit(client_id=app_id, client_secret=secret,
                              user_agent=user_agent, username=user, password=password)

    reddit.read_only = True

    reddit_web = "https://reddit.com"

    # Check if subreddit exists
    try:
        posts = []
        # If subreddit exists, search for posts
        subreddit = await reddit.subreddit(sub, fetch=True)
        count = 0

        top_posts = {'now': ("Top {num_posts} posts of the hour in r/", subreddit.top('hour', limit=num_posts + 2)),
                     'day': ("Top {num_posts} posts of the day in r/", subreddit.top('day', limit=num_posts + 2)),
                     'week': ("Top {num_posts} posts of the week in r/", subreddit.top('week', limit=num_posts + 2)),
                     'month': ("Top {num_posts} posts of the month in r/", subreddit.top('month', limit=num_posts + 2)),
                     'year': ("Top {num_posts} posts of the year in r/", subreddit.top('year', limit=num_posts + 2)),
                     'all': ("Top {num_posts} posts of all time in r/", subreddit.top('all', limit=num_posts + 2))
                     }
        embed_string = None

        if sort_by == 'hot':
            embed_string = "Top {num_posts} hottest posts in r/".format(num_posts=num_posts)
            submissions = subreddit.hot(limit=num_posts + 2)
        elif sort_by == 'rising':
            embed_string = "Top {num_posts} rising posts in r/".format(num_posts=num_posts)
            submissions = subreddit.rising(limit=num_posts + 2)
        elif sort_by == 'new':
            embed_string = "{num_posts} newest posts in r/".format(num_posts=num_posts)
            submissions = subreddit.new(limit=num_posts + 2)
        elif sort_by == 'top':
            embed_string = top_posts[top_sort][0].format(num_posts=num_posts)
            submissions = top_posts[top_sort][1]

        embed = discord.Embed(title="{embed_string}{subreddit}".format(embed_string=embed_string, subreddit=sub),
                              description=subreddit.public_description, color=0xFF5733)

        # Get the two more than the specified number of posts
        # on a subreddit to account for the maximum of 2 stickied posts
        async for submission in submissions:
            post_data = {'title': '', 'selftext': '', 'author': '', 'author_img': '',
                         'score': '', 'ratio': '', 'url': ''}

            # Get first 5 non-stickied posts off of a subreddit
            if not submission.stickied and count < num_posts:
                count += 1
                post_data['title'] = submission.title
                post_data['selftext'] = submission.selftext
                try:
                    post_data['author'] = submission.author.name
                    author = await reddit.redditor(submission.author.name, fetch=True)
                    post_data['author_img'] = author.icon_img
                except AttributeError:
                    post_data['author'] = '[deleted]'
                    post_data['author_img'] = 'https://cdn-icons-png.flaticon.com/512/1384/1384067.png'
                post_data['score'] = submission.score
                post_data['ratio'] = submission.upvote_ratio
                post_data['url'] = submission.url
                posts.append(post_data)

        await channel.send(embed=embed)
        for post in posts:
            embed = discord.Embed(title=post['title'], description=post['selftext'], color=0xFF5733)
            embed.set_author(name="u/" + post['author'], url="{}/u/{author}".format(reddit_web, author=post['author']),
                             icon_url=post['author_img'])
            if "youtube.com" in post['url']:
                embed.add_field(name="᲼᲼", value=post['url'])
                video_id = post['url'].split("v=")[1]
                video_id = video_id[0:11]
                embed.set_image(url='https://img.youtube.com/vi/{id}/hq3.jpg'.format(id=video_id))
            elif ".gifv" in post['url']:
                embed.add_field(name="᲼᲼", value=post['url'], inline=False)
            elif ".jpg" in post['url'] or ".png" in post['url'] or ".gif" in post['url']:
                embed.set_image(url=post['url'])
            else:
                embed.add_field(name="᲼᲼", value=post['url'], inline=False)
            downvotes = int(post['score']) - int(int(post['score']) * float(post['ratio']))
            embed.set_footer(text="Upvotes: " + str(post['score']) + " "*20 + "Downvotes: " + str(downvotes))
            await channel.send(embed=embed)

    # If subreddit does not exist, notify user
    except asyncprawcore.NotFound:
        await channel.send("Subreddit r/{subreddit_name} doesn't exist.".format(subreddit_name=sub))


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
                    user_message[i] = user_message[i].replace("-", " ")

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
        elif prefix + "reddit" in message.content:
            valid_sort_types = ['hot', 'new', 'top', 'rising']
            valid_top_sorts = ['now', 'day', 'week', 'month', 'year', 'all']
            user_message = message.content
            user_message = user_message.replace(prefix + "reddit", "")
            user_message = user_message.split()

            # If user input includes all 4 fields
            if len(user_message) == 4:

                # If the 'sort_by' field is valid and is not 'top'
                # remind user to check for 'help' because third field
                # only applies for 'top' posts
                if user_message[1].lower() in valid_sort_types and user_message[1].lower() != "top":
                    await channel.send("Please check j!help for proper use of this function")

                # If the 'sort_by' field is valid and is 'top'
                # check to see if 'top_sort' field is valid
                elif user_message[1].lower() in valid_sort_types and user_message[1].lower() == "top":

                    # If 'top_sort' field is valid, check if
                    # 'num_posts' field is an integer between 2-10.
                    # If invalid, remind user of valid top_sorts
                    if user_message[2].lower() in valid_top_sorts:
                        if str(user_message[3]).isnumeric():

                            # If 'num_posts' not between 2-10, use default 'num_posts'
                            # otherwise use user input
                            if int(user_message[3]) < 2 or int(user_message[3]) > 10:
                                await on_reddit(user_message[0], user_message[1].lower(), user_message[2].lower())
                            else:
                                await on_reddit(user_message[0], user_message[1].lower(),
                                                user_message[2].lower(), int(user_message[3]))
                        else:
                            await channel.send("Last value is not an integer. Please input an integer between 2 and 10")
                    else:
                        await channel.send("Not a valid sorting condition for 'Top' posts\n"
                                           "Valid conditions are: Now | Day | Week | Month | Year | All")

                # If 'sort_by' field not valid, remind user of valid sort conditions
                elif user_message[1].lower() not in valid_sort_types:
                    await channel.send(
                        "Not a valid sorting condition\nValid conditions are: Hot | New | Top | Rising")
                else:
                    await channel.send("Please check j!help for proper use of this function")
            elif len(user_message) == 3:
                if user_message[1].lower() in valid_sort_types and user_message[1].lower() != 'top':
                    if str(user_message[2]).isnumeric():
                        if int(user_message[2]) < 2 or int(user_message[2]) > 10:
                            await on_reddit(user_message[0], user_message[1].lower())
                        else:
                            await on_reddit(user_message[0], user_message[1].lower(), '', int(user_message[2]))
                    else:
                        await channel.send("Last value is not an integer. Please input an integer between 2 and 10")
                elif user_message[1].lower() in valid_sort_types and user_message[1].lower() == 'top':
                    if str(user_message[2]).isnumeric():
                        if int(user_message[2]) < 2 or int(user_message[2]) > 10:
                            await on_reddit(user_message[0], user_message[1].lower(), 'all')
                        else:
                            await on_reddit(user_message[0], user_message[1].lower(), 'all', int(user_message[2]))
                    else:
                        await channel.send("Last value is not an integer. Please input an integer between 2 and 10")
                elif user_message[1].lower() not in valid_sort_types:
                    await channel.send(
                        "Not a valid sorting condition\nValid conditions are: Hot | New | Top | Rising")
                else:
                    await channel.send("Please check j!help for proper use of this function")
            elif len(user_message) == 2:
                if user_message[1].lower() in valid_sort_types and user_message[1].lower() != 'top':
                    await on_reddit(user_message[0], user_message[1].lower())
                elif user_message[1].lower() in valid_sort_types and user_message[1].lower() == 'top':
                    await on_reddit(user_message[0], user_message[1].lower(), 'all')
                elif user_message[1].lower() not in valid_sort_types:
                    await channel.send(
                        "Not a valid sorting condition\nValid conditions are: Hot | New | Top | Rising")
                else:
                    await channel.send("Please check j!help for proper use of this function")
            elif len(user_message) == 1:
                await on_reddit(user_message[0])
            elif len(user_message) == 0:
                await on_reddit()


discordClient.run(TOKEN)
