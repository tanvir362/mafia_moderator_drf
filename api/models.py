import uuid
from django.db import models
import jsonfield
import random


class Round(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    team_id = models.CharField(max_length=150)
    channel_id = models.CharField(max_length=150)
    
    roles = jsonfield.JSONField(default=['townspeople', 'townspeople', 'townspeople', 'mafia', 'doctor', 'sheriff'])
    player_role = jsonfield.JSONField(default={})
    player_is_alive = jsonfield.JSONField(default={})
    player_vote = jsonfield.JSONField(default={})
    is_night = models.BooleanField(default=False)

    doctor_heal = models.CharField(max_length=150, blank=True, null=True)
    mafia_kill = models.CharField(max_length=150, blank=True, null=True)
    sheriff_reveal = models.CharField(max_length=150, blank=True, null=True)


    def start_night(self):
        self.doctor_heal = ""
        self.mafia_kill = ""
        self.sheriff_reveal = ""

        self.save()
        #send message to mafia channel asking mafia, sheriff, doctor to perform actions

    def start_day(self):
        killed = ''
        if self.doctor_heal != self.mafia_kill:
            if self.player_is_alive[self.mafia_kill]:
                self.player_is_alive[self.mafia_kill] = False
                killed = self.mafia_kill

        self.player_vote = {player: 0 for player in self.player_vote.keys()}
        self.save()

        # send message in mafia channel saying about what happend in past night and to start discussion 


    def assign_player_a_role(self, player):
        if player in self.player_role:
            raise Exception("You already have a role")

        if self.roles:
            role = self.roles.pop(random.randint(0, len(self.roles)-1))
            self.player_role[player] = role
            self.save()

            return role

        raise Exception("Invalid command")