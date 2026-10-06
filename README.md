# Board Game Day Date Vote Bot

A Discord bot that sets up my firend group's monthly game day vote. Once a month, it posts a poll listing every day that could work, pings everyone, and lets people vote for the days they're free.

It was built with a specific Discord server in mind, so inviting it to your server won't work unless you properly set the environment variables. I also used this bot as a chance to learn a couple of new concepts: CI/CD and logging.

## What id Does

Board game day occurs once every month, usually on a Saturday, but not always. Rather than someone remembering to set up the poll every month, the bot does it:

- **When:** at 12pm PT (Pacific Time) on the Monday 12 days before the month's first Saturday
- **Where:** a poll is set in a thread that is named in an environment variable
- **Options:** every Saturday that month, plus extra days around BC statory holidays:
  - a holiday on a _Friday_ is added as is
  - a holiday on a _Monday_ means that bot will add the _Sunday_ before it; this also includes the last day of the month is the first of the next month is a Monday holiday
- **How long:** the poll is open for one week, and people can pick as which days they are able to attend
- Pings a specific role when the poll goes out
- Picks a random title that include month from a list of potential titles
- Has a healthcheck in the form of the command `!ping` where the bot will response with `pong`

## What I Learned

### CI/CD

Every change is tested automatically, and every merge to `main` produces a ready-to-run Docker image. Both run through Github Actions.

- **CI:** runs tests on every push and pull request, installing the exact locked dependencies with `uv`
- **CD:** builds the Docker image on every push to `main` and publishes it to the Github Container Registry, taggest 'latest' and with the commit SHA.
- The Dockerfile is a multi-stage build:
  - **`deps`:** installs only the locked, non-dev dependencies into a vitual environment.
  - **`source`:** copies in just the files the bot needs at runtime.
  - **`runtime`:** starts from a slim Python image, copies in the other two stages, and runs as a non-root `app` user.

### Logging

The bot logs what it's doing so I can tell what happened without being there at noon on poll day.

- **Setup:** logging is configured once at startup, and every line shows the time, level, module and function it came from. The bot's own messages are logged from `main.py`, and `discord.py`'s logs come through in the same format.
- **Levels:** routine steps are logged at `INFO` and problems at `WARNING`. The level is set with `LOG_LEVEL` in `.env`.
- **Docker:** the bot logs to console and lets Docker collest and rotate the logs. View them with `docker compose logs -f bot`.

## Setup

### 1. Create the Discord bot

1. Create an application and bot in the [Discord Developer Portal](https://discord.com/developers/applications) and copy its token.
2. Under **Bot**, turn on the **Message Content Intent**
3. Invite the bot to your server. In the poll thread's channel, it needs to be able to view the channel, send messages in threads, send polls, and read message history (used to find the thread after Discord archives it).
4. For the ping to notify people, the role needs to be mentionable

### 2. Configure

Copy `.env.exmaple` and change its name to `.env`, then fill it in:

```sh
cp .env.exmaple .env
```

| Variable       | What it is                                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------------------------- |
| `TOKEN`        | The bot's token you generated from the Discord Developer Portal                                                     |
| `SERVER_NAME`  | Name of the Discord server                                                                                          |
| `CHANNEL_NAME` | Name of the text channel that contains the thread                                                                   |
| `THREAD_NAME`  | Name of the thread the poll is posted in. If the thread gets archived, it will still get found                      |
| `ROLE_NAME`    | Name of the role to ping                                                                                            |
| `LOG_LEVEL`    | How much you want the bot to log. Values are `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. Defaults to `INFO`. |

Note: The bot finds everything by name, so renaming the channel, thread or role in Discord means updating `.env` too.

### 3. Run

With Docker:

```sh
docker compose up -d --build
```

The container restarts on its own if it crashes or the server reboots. On startup, the bot works out which poll comes next, so a restart doesn't make it skip or repeat one. The exception is a restart after noon on poll day itself: that month's poll is skipped, because its time has already passed.

Without Docker, you need `uv` and Python 3.14:

```sh
uv sync
uv run python main.py
```

The bot shuts down cleanly on `Ctrl+C` or `docker stop`.

## Development

Run the tests:

```sh
uv run pytest
```

To change the poll titles, edit `board_game_poll_titles.txt`. Put one title per line and include `{month}` where the month's name should go. The file is read when the bot starts, so restart the bot (or rebuild the image) after editing it.
