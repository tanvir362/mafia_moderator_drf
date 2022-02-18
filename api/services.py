from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Round
from slack_sdk import WebClient
import os


@receiver(post_save, sender=Round)
def round_updates(sender, instance, **kwargs):

    print('round update receiver called')

    print(instance.player_role)
    print(kwargs)

def send_message(channel, text):
    client = WebClient(token=os.getenv('BOT_AUTH_TOKEN'))
    client.chat_postMessage(
        channel=channel,
        text=text
    )