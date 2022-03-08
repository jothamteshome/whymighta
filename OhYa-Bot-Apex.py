import disnake
import PropertiesReader
import time

from disnake.ext import commands
from aiohttp import ClientSession

prop_reader = PropertiesReader.PropertiesReader()

apex_data = {}


class ApexHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Populate Apex Dict")
    async def populate_apex(self, channel, user, platform):
        # Apex Legends API Key
        apex_api = prop_reader.get_key('APEX_API_KEY')

        # Set flag for whether to save player information or not
        keep_info = False
        player_info = {}
        uid = None

        # Make API calls with aiohttp
        async with ClientSession(trust_env=True) as session:

            # Save the time the api was last called
            player_info['last_called'] = time.monotonic()

            # Get user id from username and platform
            async with session.get('https://api.mozambiquehe.re/nametouid?player={user}&'
                                   'platform={platform}&auth={api_key}'
                                           .format(user=user, platform=platform, api_key=apex_api)) as uid_res:
                uid_data = await uid_res.json(content_type='text/plain')
                try:
                    if platform == "PC":
                        uid = uid_data['uid']
                    elif platform == "PS4" or "X1":
                        uid = uid_data['result']

                    # Get player stat data from API
                    async with session.get('https://api.mozambiquehe.re/bridge?platform={platform}&uid={uid}&auth='
                                       '{api_key}'.format(platform=platform, uid=uid,
                                                          api_key=apex_api)) as stats_res:

                        # Save specific user stats
                        stats_data = await stats_res.json(content_type='text/plain')
                        player_info['level'] = stats_data['global']['level']
                        player_info['br_rank'] = stats_data['global']['rank']['rankName'] + " " + \
                            str(stats_data['global']['rank']['rankDiv'])
                        player_info['br_score'] = stats_data['global']['rank']['rankScore']
                        player_info['arena_rank'] = stats_data['global']['arena']['rankName'] + " " + \
                            str(stats_data['global']['arena']['rankDiv'])
                        player_info['arena_score'] = stats_data['global']['arena']['rankScore']
                        player_info['current_legend'] = stats_data['legends']['selected']['LegendName']
                        player_info['legend_icon'] = stats_data['legends']['selected']['ImgAssets']['icon']

                    keep_info = True

                # If user does not exist, send chat message
                except KeyError:
                    await channel.send("{player} does not have any stats on {platform}."
                                       .format(player=user, platform=platform))
            # Close session after receiving necessary data
            await session.close()

        # Keep user info if user existed
        if keep_info:
            apex_data[(user, platform)] = player_info
        return keep_info

    @commands.command(name='Apex')
    async def apex_stats(self, channel, player, platform):
        # If user's data is already stored, check if it has been
        # 6 minutes since the last API call
        if (player, platform) in apex_data:

            # If the time since the last API call is greater than 6 minutes
            if time.monotonic() - apex_data[(player, platform)]['last_called'] > 360:

                # Update user data and send user's stats to channel
                keep_info = await self.populate_apex(channel, player, platform)
                if keep_info:
                    embed = disnake.Embed(title=player + '\'s Apex Stats', color=0x9534eb)
                    embed.add_field(name='Level', value=apex_data[(player, platform)]['level'], inline=True)
                    embed.add_field(name='Current Legend', value=apex_data[(player, platform)]['current_legend'],
                                    inline=True)
                    embed.add_field(name='BR Rank', value=apex_data[(player, platform)]['br_rank'])
                    embed.add_field(name='BR Score', value=apex_data[(player, platform)]['br_score'], inline=True)
                    embed.add_field(name='Arena Rank', value=apex_data[(player, platform)]['arena_rank'])
                    embed.add_field(name='Arena Score', value=apex_data[(player, platform)]['arena_score'], inline=True)
                    embed.set_thumbnail(apex_data[(player, platform)]['legend_icon'])
                    await channel.send(embed=embed)

            # If it has not been over 6 minutes since last API call for this user,
            # send previously saved stats to channel
            else:
                embed = disnake.Embed(title=player + '\'s Apex Stats', color=0x9534eb)
                embed.add_field(name='Level', value=apex_data[(player, platform)]['level'], inline=True)
                embed.add_field(name='Current Legend', value=apex_data[(player, platform)]['current_legend'],
                                inline=True)
                embed.add_field(name='BR Rank', value=apex_data[(player, platform)]['br_rank'])
                embed.add_field(name='BR Score', value=apex_data[(player, platform)]['br_score'], inline=True)
                embed.add_field(name='Arena Rank', value=apex_data[(player, platform)]['arena_rank'])
                embed.add_field(name='Arena Score', value=apex_data[(player, platform)]['arena_score'], inline=True)
                embed.set_thumbnail(apex_data[(player, platform)]['legend_icon'])
                await channel.send(embed=embed)
        else:

            # If user's data is not already stored, fetch
            # user's data and send stats to channel
            keep_info = await self.populate_apex(channel, player, platform)
            if keep_info:
                embed = disnake.Embed(title=player + '\'s Apex Stats', color=0x9534eb)
                embed.add_field(name='Level', value=apex_data[(player, platform)]['level'], inline=True)
                embed.add_field(name='Current Legend', value=apex_data[(player, platform)]['current_legend'],
                                inline=True)
                embed.add_field(name='BR Rank', value=apex_data[(player, platform)]['br_rank'])
                embed.add_field(name='BR Score', value=apex_data[(player, platform)]['br_score'], inline=True)
                embed.add_field(name='Arena Rank', value=apex_data[(player, platform)]['arena_rank'])
                embed.add_field(name='Arena Score', value=apex_data[(player, platform)]['arena_score'], inline=True)
                embed.set_thumbnail(apex_data[(player, platform)]['legend_icon'])
                await channel.send(embed=embed)

    @commands.command(name='Apex Message')
    async def apex_message(self, message):
        check_help = False
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "apex", "")
        user_message = user_message.split()
        # If there are two parameters, call stats function, otherwise advise
        # user to check help message
        if len(user_message) == 2:
            await self.apex_stats(message.channel, user_message[0], user_message[1].upper())
        else:
            check_help = True

        if check_help:
            await message.channel.send("Please check j!help for proper use of this function")


def setup(bot):
    bot.add_cog(ApexHandler(bot))
