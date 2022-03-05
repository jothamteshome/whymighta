import disnake
import PropertiesReader
import asyncpraw
import asyncprawcore

from disnake.ext import commands

prop_reader = PropertiesReader.PropertiesReader()

defaults = ('itswiggles_', 'hot', '', 5)


class RedditHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='on_reddit')
    async def on_reddit(self, sub=defaults[0], sort_by=defaults[1], top_sort=defaults[2], num_posts=defaults[3]):
        # Get Discord channel
        channel_id = prop_reader.get('DISCORD_CHANNEL')
        channel = await self.bot.fetch_channel(channel_id)

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

            embed = disnake.Embed(title="{embed_string}{subreddit}".format(embed_string=embed_string, subreddit=sub),
                                  description=subreddit.public_description, color=0xFF5733)

            # Get the two more than the specified number of posts
            # on a subreddit to account for the maximum of 2 stickied posts
            async for submission in submissions:
                post_data = {'title': '', 'selftext': '', 'author': '', 'author_img': '',
                             'score': '', 'ratio': '', 'url': '', 'permalink': ''}

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
                    post_data['permalink'] = submission.permalink
                    posts.append(post_data)

            await channel.send(embed=embed)
            for post in posts:

                # Create an embed for each post containing its title and text
                embed = disnake.Embed(title=post['title'], description=post['selftext'],
                                      color=0xFF5733, url=post['url'])

                # Set the author to the creator of the reddit post and add a link to their profile
                if post['author'] == '[deleted]':
                    embed.set_author(name="u/" + post['author'], url="https://bitly.com/98K8eH",
                                     icon_url=post['author_img'])
                else:
                    embed.set_author(name="u/" + post['author'],
                                     url="{}/u/{author}".format(reddit_web, author=post['author']),
                                     icon_url=post['author_img'])
                if "youtube.com" in post['url']:
                    embed.url = post['url']
                    video_id = post['url'].split("v=")[1]
                    video_id = video_id[0:11]
                    embed.set_image(url='https://img.youtube.com/vi/{id}/hq3.jpg'.format(id=video_id))
                elif ".gifv" in post['url']:
                    embed.url = reddit_web + post['permalink']
                elif ".jpg" in post['url'] or ".png" in post['url'] or ".gif" in post['url']:
                    embed.set_image(url=post['url'])
                    embed.url = reddit_web + post['permalink']
                else:
                    embed.url = reddit_web + post['permalink']
                downvotes = int(post['score']) - int(int(post['score']) * float(post['ratio']))
                embed.set_footer(text="Upvotes: " + str(post['score']) + " " * 20 + "Downvotes: " + str(downvotes))
                await channel.send(embed=embed)

        # If subreddit does not exist, notify user
        except asyncprawcore.NotFound:
            await channel.send("Subreddit r/{subreddit_name} doesn't exist.".format(subreddit_name=sub))
        except asyncprawcore.exceptions.Redirect:
            await channel.send("Subreddit r/{subreddit_name} doesn't exist.".format(subreddit_name=sub))

    @commands.command('on_reddit_message')
    async def on_reddit_message(self, message):
        channel = message.channel
        valid_sort_types = ['hot', 'new', 'top', 'rising']
        valid_top_sorts = ['now', 'day', 'week', 'month', 'year', 'all']
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "reddit", "")
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
                            await channel.send("Last value must be an integer between 2 and 10")
                        else:
                            await self.on_reddit(user_message[0], user_message[1].lower(),
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
                        await channel.send("Last value must be an integer between 2 and 10")
                    else:
                        await self.on_reddit(user_message[0], user_message[1].lower(), '', int(user_message[2]))
                else:
                    await channel.send("Last value is not an integer. Please input an integer between 2 and 10")
            elif user_message[1].lower() in valid_sort_types and user_message[1].lower() == 'top':
                if str(user_message[2]).isnumeric():
                    if int(user_message[2]) < 2 or int(user_message[2]) > 10:
                        await channel.send("Last value must be an integer between 2 and 10")
                    else:
                        await self.on_reddit(user_message[0], user_message[1].lower(), 'all', int(user_message[2]))
                elif user_message[2].lower() in valid_top_sorts:
                    await self.on_reddit(user_message[0], user_message[1].lower(), user_message[2].lower())
                else:
                    await channel.send("Please check j!help for proper use of this function")
            elif user_message[1].lower() not in valid_sort_types:
                await channel.send(
                    "Not a valid sorting condition\nValid conditions are: Hot | New | Top | Rising")
            else:
                await channel.send("Please check j!help for proper use of this function")
        elif len(user_message) == 2:
            if user_message[1].lower() in valid_sort_types and user_message[1].lower() != 'top':
                await self.on_reddit(user_message[0], user_message[1].lower())
            elif user_message[1].lower() in valid_sort_types and user_message[1].lower() == 'top':
                await self.on_reddit(user_message[0], user_message[1].lower(), 'all')
            elif user_message[1].lower() not in valid_sort_types:
                await channel.send(
                    "Not a valid sorting condition\nValid conditions are: Hot | New | Top | Rising")
            else:
                await channel.send("Please check j!help for proper use of this function")
        elif len(user_message) == 1:
            await self.on_reddit(user_message[0])
        elif len(user_message) == 0:
            await self.on_reddit(defaults[0])


def setup(bot):
    bot.add_cog(RedditHandler(bot))
