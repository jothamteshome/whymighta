import random
import whymightaGlobalVariables
import whymightaSupportFunctions

from transformers import AutoModelForCausalLM, AutoTokenizer

# Load tokenizer and models from Hugging Face
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
main_model = AutoModelForCausalLM.from_pretrained("jothamteshome/whymightaMainChatbotModel")
backup_model = AutoModelForCausalLM.from_pretrained("jothamteshome/whymightaBackupChatbotModel")


# Process the input of the main_model to fit the data it was trained on
def preprocessInput(message, guild_usernames):
    # Remove initial mention to the bot
    content = message.content.replace(whymightaGlobalVariables.bot.user.mention, "", 1).lstrip()

    # For any mention in the message, replace with <discord_mention> token
    for member in message.mentions:
        content = content.replace(member.mention, "<discord_mention>")

    # For any username in the message, replace with <discord_username> token
    for username in guild_usernames:
        if username in content:
            content = content.replace(username, "<discord_username>")

    return content


# Process the output of the main_model to fit a more natural conversation structure
def processModelOutput(chatbot_reply, guild_mentions, guild_usernames, guild_emotes, author):
    # Count the amount of times tokens appear
    mention_count = chatbot_reply.count("<discord_mention>")
    username_count = chatbot_reply.count("<discord_username>")
    emote_count = chatbot_reply.count("<discord_emote>")

    # Replace mention tokens with a mention of a server member
    chatbot_reply = whymightaSupportFunctions.replaceTokens("<discord_mention>",
                                                            mention_count, guild_mentions, author, chatbot_reply)

    # Replace username tokens with a username of a server member
    chatbot_reply = whymightaSupportFunctions.replaceTokens("<discord_username>",
                                                            username_count, guild_usernames, author, chatbot_reply)

    # Replace emote tokens with a random emoji from the server
    for i in range(emote_count):
        chatbot_reply = chatbot_reply.replace("<discord_emote>", guild_emotes[random.randint(1, len(guild_emotes) - 1)])

    # Replace escaped newlines with true newline characters
    chatbot_reply = chatbot_reply.replace("\\n", "\n")

    # If the message only consists of a mention, skip the message
    sans_mentions = chatbot_reply

    for mention in guild_mentions:
        sans_mentions = sans_mentions.replace(mention, "").lstrip()

    if len(sans_mentions) == 0:
        return None

    return chatbot_reply


async def chatting(message):
    # Collect guild information
    guild_mentions = [member.mention for member in message.guild.members if not member.bot]
    guild_usernames = [member.display_name for member in message.guild.members if not member.bot]
    guild_emotes = [":smile:", ":frown:"]

    # Add server emojis if they exist
    if len(message.guild.emojis) > 0:
        guild_emotes.extend([message.guild.emojis])

    # Preprocess user input before feeding to main_model for generation
    message_content = preprocessInput(message, guild_usernames)

    # Tokenize message content
    new_user_input_ids = tokenizer.encode(message_content + tokenizer.eos_token, return_tensors='pt')

    # Generate a response while limiting the total chat history to 1000 tokens,
    main_model_output = main_model.generate(new_user_input_ids,
                                            max_new_tokens=1000, pad_token_id=tokenizer.eos_token_id)
    backup_model_output = backup_model.generate(new_user_input_ids,
                                                max_new_tokens=1000, pad_token_id=tokenizer.eos_token_id)

    # Decode tokenized message to receive models text output
    main_reply = tokenizer.decode(main_model_output[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)
    backup_reply = tokenizer.decode(backup_model_output[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)

    # Process the models output
    chatbot_reply = processModelOutput(main_reply, guild_mentions, guild_usernames, guild_emotes, message.author)

    # If the main model gives a bad output, try with the backup model
    if chatbot_reply is None:
        chatbot_reply = processModelOutput(backup_reply, guild_mentions, guild_usernames, guild_emotes, message.author)

    # If the reply has content aside from a single mention, send it
    if chatbot_reply is not None:
        await message.channel.send(chatbot_reply)
