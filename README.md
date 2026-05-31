# Whymighta

A feature-rich Discord bot with AI-powered conversation, a global XP leveling system, server theming, games management, and more — built with Python and Disnake.

## Features

- **AI Chat** — Mention the bot or open a private thread to have a conversation powered by OpenAI (GPT-4) or Anthropic (Claude)
- **Global XP & Leaderboards** — Earn XP across all servers; view per-guild leaderboards with pagination
- **Server Theming** — Bulk-assign nicknames from a JSON theme file, toggle roleplay mode, and export current nicknames
- **Games List** — Maintain a per-guild game library and randomly pick what to play next
- **Fortnite Drop Picker** — Randomly selects a drop location for Fortnite sessions
- **Jail Meme Generator** — Composite a user's avatar behind bars using Pillow
- **Weather** — Look up current weather for any city with F, C, or K units
- **Mock & Binary Modes** — Automatically transform messages in a channel for fun
- **Admin Tools** — Sync/clear Discord slash commands, hot-reload cogs at runtime

## Prerequisites

- Python 3.13+
- PostgreSQL
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- At least one LLM API key: [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/)
- [OpenWeatherMap](https://openweathermap.org/api) API key (for `/weather`)

## Installation

```bash
git clone https://github.com/jothamteshome/whymighta.git
cd whymighta
pip install -e .
```

## Configuration

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from Discord Developer Portal |
| `DB_USERNAME` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `DB_DATABASE` | PostgreSQL database name |
| `OPENAI_API_KEY` | OpenAI API key (optional if using Anthropic) |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional if using OpenAI) |
| `OPENAI_MODEL` | OpenAI model name (default: `gpt-4.1-mini`) |
| `ANTHROPIC_MODEL` | Anthropic model name (default: `claude-haiku-4-5`) |
| `WEATHER_API_KEY` | OpenWeatherMap API key |

## Running

```bash
python main.py
```

The bot will initialize the database schema, load all cogs, and connect to Discord automatically.

## Docker

```bash
docker-compose up -d
```

The compose file expects a `.env` file in the project root and connects to an external Docker network named `local-services`.

## Commands

### 💬 Chat
| Command | Description |
|---|---|
| `/chat new_session` | Open a private thread with the bot |
| `/chat end_session` | Close your chat thread |

### ⚙️ Server
| Command | Description |
|---|---|
| `/server` | Show bot status for this guild (admin) |
| `/theme apply` | Upload a JSON theme file to assign nicknames (admin) |
| `/theme export` | Export current nicknames as JSON (admin) |
| `/theme clear` | Remove the active theme (admin) |
| `/theme roleplay` | Toggle roleplay mode on/off (admin) |

### 🎮 Games
| Command | Description |
|---|---|
| `/games list` | Show all games in the guild list |
| `/games add <name>` | Add a game |
| `/games remove <name>` | Remove a game |
| `/games choose` | Randomly pick a game |
| `/fortnite drop` | Random Fortnite drop location |

### 🛠️ Utilities
| Command | Description |
|---|---|
| `/ping` | Check bot latency |
| `/level` | View your XP and level progress |
| `/leaderboard` | View the guild XP leaderboard |

### 🎲 Misc
| Command | Description |
|---|---|
| `/jail <user>` | Generate a jail meme for a user |
| `/weather <city> <units>` | Get current weather |

### /help
Run `/help` in Discord to browse all commands interactively.

## Project Structure

```
whymighta/
├── main.py               # Entry point
├── core/config.py        # Pydantic settings loader
├── cogs/                 # Bot command modules
├── database/             # Async PostgreSQL client + repositories
├── llm/                  # OpenAI / Anthropic abstraction layer
├── models/               # Pydantic data models
├── utils/                # Shared utilities
└── views/                # Discord UI components
```
