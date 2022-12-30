import disnake
import PropertiesReader
import time

from aiohttp import ClientSession

prop_reader = PropertiesReader.PropertiesReader()

apex_data = {}

# Convert rank to roman numeral
roman_numerals = {1: "I", 2: "II", 3: "III", 4: "IV"}


class ApexHandler:
    def __init__(self, bot):
        self.bot = bot

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
                                   'platform={platform}&auth={api_key}'.format(user=user, platform=platform,
                                                                               api_key=apex_api)) as uid_res:
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
                        if stats_data['global']['rank']['rankName'] == "Unranked":
                            player_info['br_rank'] = stats_data['global']['rank']['rankName']
                        else:
                            player_info['br_rank'] = stats_data['global']['rank']['rankName'] + " " + \
                                                     roman_numerals[stats_data['global']['rank']['rankDiv']]
                        player_info['br_score'] = stats_data['global']['rank']['rankScore']
                        if stats_data['global']['arena']['rankName'] == "Unranked":
                            player_info['arena_rank'] = stats_data['global']['arena']['rankName']
                        else:
                            player_info['arena_rank'] = stats_data['global']['arena']['rankName'] + " " + \
                                                        roman_numerals[stats_data['global']['arena']['rankDiv']]
                        player_info['arena_score'] = stats_data['global']['arena']['rankScore']
                        player_info['current_legend'] = stats_data['legends']['selected']['LegendName']

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

    async def apex_stats(self, channel, player, platform):
        embed = disnake.Embed(title=player + '\'s Apex Stats', description="-" * 40, color=0x9534eb)
        # If user's data is already stored, check if it has been
        # 6 minutes since the last API call
        if (player, platform) in apex_data:

            # If the time since the last API call is greater than 6 minutes
            if time.monotonic() - apex_data[(player, platform)]['last_called'] > 360:

                # Update user data and send user's stats to channel
                keep_info = await self.populate_apex(channel, player, platform)
                if keep_info:
                    embed.add_field(name='Level', value=apex_data[(player, platform)]['level'], inline=True)
                    embed.add_field(name='Current Legend', value=apex_data[(player, platform)]['current_legend'],
                                    inline=True)
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    embed.add_field(name='BR Rank', value=apex_data[(player, platform)]['br_rank'], inline=True)
                    embed.add_field(name='BR Score', value=apex_data[(player, platform)]['br_score'], inline=True)
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    embed.add_field(name='Arena Rank', value=apex_data[(player, platform)]['arena_rank'], inline=True)
                    embed.add_field(name='Arena Score', value=apex_data[(player, platform)]['arena_score'], inline=True)
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    await channel.send(embed=embed)

            # If it has not been over 6 minutes since last API call for this user,
            # send previously saved stats to channel
            else:
                embed.add_field(name='Level', value=apex_data[(player, platform)]['level'], inline=True)
                embed.add_field(name='Current Legend', value=apex_data[(player, platform)]['current_legend'],
                                inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name='BR Rank', value=apex_data[(player, platform)]['br_rank'], inline=True)
                embed.add_field(name='BR Score', value=apex_data[(player, platform)]['br_score'], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name='Arena Rank', value=apex_data[(player, platform)]['arena_rank'], inline=True)
                embed.add_field(name='Arena Score', value=apex_data[(player, platform)]['arena_score'], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                await channel.send(embed=embed)
        else:

            # If user's data is not already stored, fetch
            # user's data and send stats to channel
            keep_info = await self.populate_apex(channel, player, platform)
            if keep_info:
                embed.add_field(name='Level', value=apex_data[(player, platform)]['level'], inline=True)
                embed.add_field(name='Current Legend', value=apex_data[(player, platform)]['current_legend'],
                                inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name='BR Rank', value=apex_data[(player, platform)]['br_rank'], inline=True)
                embed.add_field(name='BR Score', value=apex_data[(player, platform)]['br_score'], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name='Arena Rank', value=apex_data[(player, platform)]['arena_rank'], inline=True)
                embed.add_field(name='Arena Score', value=apex_data[(player, platform)]['arena_score'], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                await channel.send(embed=embed)

    async def apex_map(self, channel):
        # Get the Apex Legends API Key
        api_key = prop_reader.get_key('APEX_API_KEY')

        # Create an embed to add map rotation data to
        embed = disnake.Embed(title="Map Rotation", description="-" * 50, color=0x9534eb)

        # Make API calls with aiohttp
        async with ClientSession(trust_env=True) as session:
            async with session.get('https://api.mozambiquehe.re/maprotation?version=2&auth={api_key}'
                                           .format(api_key=api_key)) as rotation_res:
                rotation_data = await rotation_res.json(content_type='text/plain')

                # Add specific data to embed
                embed.add_field(name="Battle Royale", value=rotation_data["battle_royale"]["current"]["map"],
                                inline=True)
                embed.add_field(name="Next Map", value=rotation_data["battle_royale"]["next"]["map"], inline=True)
                embed.add_field(name="Time Left", value=rotation_data["battle_royale"]["current"]["remainingTimer"],
                                inline=True)
                embed.add_field(name="Arenas", value=rotation_data["arenas"]["current"]["map"], inline=True)
                embed.add_field(name="Next Map", value=rotation_data["arenas"]["next"]["map"], inline=True)
                embed.add_field(name="Time Left", value=rotation_data["arenas"]["current"]["remainingTimer"],
                                inline=True)
                embed.add_field(name="Ranked BR", value=rotation_data["ranked"]["current"]["map"],
                                inline=True)
                embed.add_field(name="Next Map", value=rotation_data["ranked"]["next"]["map"], inline=True)
                embed.add_field(name="\u200b", value="\u200b", inline=True)
                embed.add_field(name="Ranked Arenas", value=rotation_data["arenasRanked"]["current"]["map"],
                                inline=True)
                embed.add_field(name="Next Map", value=rotation_data["arenasRanked"]["next"]["map"], inline=True)
                embed.add_field(name="Time Left", value=rotation_data["arenasRanked"]["current"]["remainingTimer"],
                                inline=True)

            # Close aiohttp session
            await session.close()

        # Send embed with map data to channel
        await channel.send(embed=embed)

    async def apex_message(self, message):
        check_help = False
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "apex", "")
        user_message = user_message.split()
        # If there are two parameters, call stats function, otherwise advise
        # user to check help message
        if len(user_message) == 3:
            if user_message[0] == "stats":
                await self.apex_stats(message.channel, user_message[1], user_message[2].upper())
            else:
                check_help = True
        elif len(user_message) == 1:

            # If user input is 'map', get map data
            if user_message[0] == "map":
                await self.apex_map(message.channel)
            else:
                check_help = True

        else:
            check_help = True

        if check_help:
            await message.channel.send("Please check j!help for proper use of this function")
