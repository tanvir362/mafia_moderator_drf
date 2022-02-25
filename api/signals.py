from django.db.models.signals import post_save
from api.models import Round
from django.dispatch import receiver

@receiver(post_save, sender=Round)
def round_updates(sender, instance, **kwargs):

    print('round update receiver called')

    print(instance.player_role)
    print(kwargs)