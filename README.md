# YouTube to Discord Notifier

A Python script that monitors YouTube channels via RSS feeds and sends Discord webhook notifications when new videos are uploaded.

## Features

- Monitor multiple YouTube channels
- Send Discord webhook notifications with video embeds
- State management to prevent duplicate notifications
- Designed to run on a schedule (systemd, cron, etc.)

## Setup

1. Install dependencies using `uv`:
```sh
uv sync
```

2. Create a configuration file:
```sh
cp config.example.yaml config.yaml
```

3. Edit `config.yaml` with your Discord webhook URL and YouTube channels:
   - Get your Discord webhook URL from Server Settings → Integrations → Webhooks
   - Find YouTube channel IDs by visiting a channel page and looking at the URL or page source

## Configuration

The `config.yaml` file has the following structure:

```yaml
discord_webhook_url: "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

channels:
  - id: "YOUTUBE_CHANNEL_ID"
    name: "Channel Display Name"
  
  - id: "ANOTHER_CHANNEL_ID"
    name: "Another Channel"
```

### Finding YouTube Channel IDs

- Visit the channel page
- If the URL is `youtube.com/@username`, view the page source and search for `"channelId"`
- If the URL is `youtube.com/channel/CHANNEL_ID`, the ID is in the URL

## Usage

Run the script manually:
```sh
uv run main.py
```

On first run, the script initializes state with the latest video from each channel without sending notifications. Subsequent runs will notify about new videos.

### Command Line Options

```sh
uv run main.py --help
```

- `--config PATH`: Specify a custom config file path (default: `config.yaml`)
- `--state PATH`: Specify a custom state file path (default: `state.json`)

Example:
```sh
uv run main.py --config /path/to/config.yaml --state /path/to/state.json
```

## Systemd Setup

Create a systemd service file at `~/.config/systemd/user/yt-to-discord.service`:

```ini
[Unit]
Description=YouTube to Discord Notifier
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/yt-to-discord
ExecStart=/usr/bin/uv run main.py

[Install]
WantedBy=default.target
```

Create a timer file at `~/.config/systemd/user/yt-to-discord.timer`:

```ini
[Unit]
Description=Run YouTube to Discord Notifier every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

Enable and start the timer:
```sh
systemctl --user enable yt-to-discord.timer
systemctl --user start yt-to-discord.timer
```

Check status:
```sh
systemctl --user status yt-to-discord.timer
systemctl --user list-timers
```

## State Management

The script maintains a `state.json` file that tracks the last seen video ID for each channel. This prevents duplicate notifications. The state file is created automatically on first run.

## License

See LICENSE file.