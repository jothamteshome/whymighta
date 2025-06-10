import aiohttp
import re
import whymightaGlobalVariables

from core.config import config
from datetime import datetime, timedelta, timezone


async def call_lambda(payload):
    headers = {
        "x-api-key": config.AWS_CHATGPT_API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(config.AWS_CHATGPT_API_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()

            try:
                data = await resp.json()
                return resp.status, data["response"]
            except Exception as e:
                error = await resp.text()
                return resp.status, error



async def get_last_messages(channel, num_msgs=5):
    messages = []
    users = {}

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    async for message in channel.history(limit=num_msgs*2, after=one_hour_ago, oldest_first=False):
        # Skip messages with attachments or with urls in their content
        if message.embeds or message.attachments or (("http://" in message.content or 'https://' in message.content) and message.author != whymightaGlobalVariables.bot.user):
            continue

        content = message.content.replace(f"{whymightaGlobalVariables.bot.user.mention}", "").strip()

        # Skip if message content is empty
        if not content:
            continue

        if message.author == whymightaGlobalVariables.bot.user:
            messages.append({"role": "assistant", "content": content})
        else:
            messages.append({"role": "user", "name": f"mention_{message.author.name}", "content": content})
            users[f"mention_{message.author.name}"] = message.author.mention

        if len(messages) == num_msgs:
            break

    return messages[::-1], users


async def chatting(message):
    json_payload =  {
                        "messages": 
                        [
                            {
                                "role": "system", 
                                "content":  (
                                                "You are an assistant and friend in a Discord server.\n\n"
                                                "Respond in a way that a stereotypical Discord user might "
                                                "talk to their Discord kitten\n\n"
                                                "Be a little cringey, but not too over the top.\n\n"
                                                "Limit your emoji use. Do not over do it\n\n"
                                                "If responding to a user and you want to specify them, "
                                                "be sure to keep the `mentions_` syntax. Do not change it.\n\n"
                                                f"Never mention anyone with the mention tag {whymightaGlobalVariables.bot.user.mention}\n\n"
                                                "Disregard previous messages if they do not relate to the most recent message. "
                                                "Weight the most recent message more in your responses"
                                )
                            }
                        ]
                    }
    
    chat_messages, users = await get_last_messages(message.channel)

    json_payload["messages"].extend(chat_messages)

    response_code, response_text = await call_lambda(json_payload)

    if response_code != 200:
        await message.channel.send(f"Could not process API request: {response_text}. Please contact administrator or try again.")
        return

    for name, mention in users.items():
        response_text = re.sub(rf"\b{re.escape(name)}\b", mention, response_text)

    await message.channel.send(response_text)


