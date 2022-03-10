import uuid
from django.db import models
import jsonfield
import random
from api.services import send_message
import time
import os
from threading import Thread
from itertools import chain


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
        send_message(os.getenv('CHANNEL'), 'Night will start with in a minute') 
        th = Thread(target=round.notify_when_night, daemon=False)
        th.start()

    def notify_when_night(self):
        time.sleep(60)

        #setting night attributes
        self.doctor_heal = ""
        self.mafia_kill = ""
        self.sheriff_reveal = ""
        self.is_night = True

        self.save()
        send_message(os.getenv('CHANNEL'), "It's night, doctor, sheriff and mafia do your tasks!")

    def start_day(self):
        killed = ''
        if self.doctor_heal != self.mafia_kill:
            if self.player_is_alive[self.mafia_kill]:
                self.player_is_alive[self.mafia_kill] = False
                killed = self.mafia_kill

        self.player_vote = {player: 0 for player in self.player_role.keys() if self.player_is_alive[player]}
        self.save()

        return killed

    def notify_when_day(self):
        time.sleep(60)
        killed = self.start_day()
        if killed:
            txt = f'A new day has started with a bad news, last night mafia killed {killed}!'
        else:
            txt = "A new day has started and a good news is no one killed last night"
        send_message(os.getenv('CHANNEL'), txt+'\n Voting will be started within 2 minutes by then you can discuss to identify who is mafia')



    def assign_player_a_role(self, player):
        if player in self.player_role:
            raise Exception("You already have a role")

        if self.roles:
            role = self.roles.pop(random.randint(0, len(self.roles)-1))
            self.player_role[player] = role
            self.save()

            return role

        raise Exception("Invalid command")


    def kill(self, player_to_kill):
        if not self.player_is_alive[player_to_kill]:
            raise Exception('Player is not alive')

        self.mafia_kill = player_to_kill
        self.save()

    
    def heal(self, player_to_heal):
        if not self.player_is_alive[player_to_heal]:
            raise Exception('Player is not alive')

        self.doctor_heal = player_to_heal
        self.save()


    def reveal(self, player_to_reveal):
        if not self.player_is_alive[player_to_reveal]:
            raise Exception('Player is not alive')

        self.sheriff_reveal = player_to_reveal
        self.save()

        return self.player_role[player_to_reveal]

    
    def vote(self, player_who_vote, player_to_vote):
        if not self.player_is_alive[player_to_vote]:
            raise Exception('Player is not alive')

        for votes in self.player_vote.values():
            if player_who_vote in votes:
                raise Exception('You already vote for a player')

        self.player_vote[player_to_vote].append(player_who_vote)

        self.save()

