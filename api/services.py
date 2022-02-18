from slack_sdk import WebClient
import os


def send_message(channel, text):
    client = WebClient(token=os.getenv('BOT_AUTH_TOKEN'))
    client.chat_postMessage(
        channel=channel,
        text=text
    )