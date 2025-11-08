from random import randint, shuffle
import sys
import json
import asyncio
from pathlib import Path
from textwrap import shorten
from typing import TypedDict

import yaml
import click
from aiohttp import ClientSession


class VideoInfo(TypedDict):
    id: str
    title: str
    link: str
    author: str
    author_url: str
    published: str
    thumbnail: str
    channel_name: str
    description: str


class ChannelState(TypedDict):
    last_video_id: str | None


class ChannelConfig(TypedDict):
    id: str
    name: str


class Config(TypedDict):
    discord_webhook_url: str
    channels: list[ChannelConfig]


class YouTubeMonitor:
    def __init__(self, config_path: str, state_path: str) -> None:
        self.config_path = Path(config_path)
        self.state_path = Path(state_path)
        self.config = self._load_config()
        self.state = self._load_state()

    def _load_config(self) -> Config:
        if not self.config_path.exists():
            click.echo(f"Error: Config file not found at {self.config_path}", err=True)
            sys.exit(1)

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def _load_state(self) -> dict[str, ChannelState]:
        if not self.state_path.exists():
            return {}

        with open(self.state_path, "r") as f:
            return json.load(f)

    def _save_state(self) -> None:
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=2)

    def _get_channel_feed(self, channel_id: str) -> object | None:
        import feedparser

        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            feed = feedparser.parse(feed_url)
            return feed
        except Exception as e:
            click.echo(f"Error fetching feed for {channel_id}: {e}", err=True)
            return None

    async def _send_discord_webhook(
        self, session: ClientSession, webhook_url: str, video: VideoInfo
    ) -> None:  # type: ignore
        embed = {
            "title": video["title"],
            "url": video["link"],
            "description": video["description"],
            "color": 16711680,
            "timestamp": video["published"],
            "image": {"url": video.get("thumbnail", "")},
            "author": {"name": video["author"], "url": video["author_url"]},
        }

        payload = {"embeds": [embed]}

        try:
            async with session.post(webhook_url, json=payload) as response:
                response.raise_for_status()
                click.echo(f"Sent notification for: {video['title']}")
        except Exception as e:
            click.echo(f"Error sending webhook: {e}", err=True)

    def _parse_video(self, entry: object, channel_name: str) -> VideoInfo:
        video_id = getattr(
            entry, "yt_videoid", getattr(entry, "link", "").split("v=")[-1]
        )

        thumbnail = ""
        if hasattr(entry, "media_thumbnail"):
            media_thumb = getattr(entry, "media_thumbnail")
            if media_thumb:
                thumbnail = media_thumb[0]["url"]

        author_url = ""
        if hasattr(entry, "author_detail"):
            author_detail = getattr(entry, "author_detail")
            if hasattr(author_detail, "href"):
                author_url = author_detail.href

        description = ""
        if hasattr(entry, "summary"):
            description = getattr(entry, "summary")

        return VideoInfo(
            id=video_id,
            title=getattr(entry, "title", ""),
            link=getattr(entry, "link", ""),
            author=getattr(entry, "author", ""),
            author_url=author_url,
            published=getattr(entry, "published", ""),
            thumbnail=thumbnail,
            channel_name=channel_name,
            description=shorten(description, width=200, placeholder="..."),
        )

    async def check_channels(self) -> None:
        channels = self.config.get("channels", [])
        webhook_url = self.config.get("discord_webhook_url")

        if not webhook_url:
            click.echo("Error: discord_webhook_url not configured", err=True)
            sys.exit(1)

        shuffle(channels)
        async with ClientSession() as session:
            for channel in channels:
                channel_id = channel.get("id")
                channel_name = channel.get("name", "Unknown")

                if not channel_id:
                    click.echo(f"Skipping channel without ID: {channel_name}")
                    continue

                click.echo(f"Checking channel: {channel_name} ({channel_id})")

                feed = self._get_channel_feed(channel_id)
                if not feed or not hasattr(feed, "entries"):
                    click.echo(f"No entries found for {channel_name}")
                    continue

                entries = getattr(feed, "entries", [])
                if not entries:
                    click.echo(f"No entries found for {channel_name}")
                    continue

                if channel_id not in self.state:
                    self.state[channel_id] = ChannelState(last_video_id=None)

                last_video_id = self.state[channel_id]["last_video_id"]
                new_videos: list[VideoInfo] = []

                for entry in entries:
                    video = self._parse_video(entry, channel_name)

                    if last_video_id is None:
                        self.state[channel_id]["last_video_id"] = video["id"]
                        click.echo(
                            f"Initialized state for {channel_name} with video: {video['title']}"
                        )

                    if video["id"] == last_video_id:
                        break

                    self._save_state()
                    new_videos.append(video)

                for video in new_videos[:1]:
                    if "shorts" not in video["link"]:
                        await self._send_discord_webhook(session, webhook_url, video)
                    self.state[channel_id]["last_video_id"] = video["id"]
                    await asyncio.sleep(randint(5, 60))




@click.command()
@click.option("--config", default="config.yaml", help="Path to config file")
@click.option("--state", default="state.json", help="Path to state file")
def main(config: str, state: str) -> None:
    monitor = YouTubeMonitor(config_path=config, state_path=state)
    asyncio.run(monitor.check_channels())
