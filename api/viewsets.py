from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
import os
from django.conf import settings
from api.models import Round
from api.services import send_message
from threading import Thread
import json


class SlackAppViewset(viewsets.ViewSet):
    permission_classes=[AllowAny]

    def get_serializer_class(self, *args, **kwargs):
        pass
    
    @action(methods=['POST'], detail=False)
    def new_round(self, request, *args, **kwargs):
        payload = request.data
        print(payload)
        team = payload["team_id"]
        
        if Round.objects.filter(team_id=team).exists():
            send_message(
                channel=os.getenv('CHANNEL'),
                text="A round is going on"
            )

        else:

            round = Round.objects.create(
                team_id = team,
                channel_id = payload["channel_id"]
            )

            send_message(
                channel=os.getenv('CHANNEL'),
                text="New round started.\nEveryone, please run /my_role command to get your role"
            )
        
        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def my_role(self, request, *args, **kwargs):
        payload = request.data
        print(payload)

        round = Round.objects.get(team_id=payload["team_id"])
        player = payload["user_id"]

        try:

            role = round.assign_player_a_role(player)

            send_message(player, role)

            if not round.roles:
                round.start_night()

        except Exception as e:
            send_message(player, str(e))
        
        print('task done')
        return Response(status=status.HTTP_200_OK)

    
    @action(methods=['POST'], detail=False)
    def kill(self, request, *args, **kwargs):
        payload = request.data
        print(json.dumps(payload, indent=2))

        try:
            round = Round.objects.get(team_id=payload["team_id"])
            player = payload["user_id"]
            player_to_kill = payload["text"].split('|')[0].split('@')[1]

            if not round.player_is_alive[player]:
                raise Exception("You can't perform any task, you are not alive")
            
            if not round.is_night:
                raise Exception("It's not night yet")

            if round.player_role[player] != "mafia":
                raise Exception("You can't kill a player as you'r not a mafia")

            round.kill(player_to_kill)

            if round.is_night_ends:
                round.start_day()
                
            send_message(player, text="Wait to see if the victim is killed")
        except Exception as e:
            send_message(player, text=str(e))

        return Response(status=status.HTTP_200_OK)


    @action(methods=['POST'], detail=False)
    def heal(self, request, *args, **kwargs):
        payload = request.data
        print(json.dumps(payload, indent=2))

        try:
            round = Round.objects.get(team_id=payload["team_id"])
            player = payload["user_id"]
            player_to_heal = payload["text"].split('|')[0].split('@')[1]

            if not round.player_is_alive[player]:
                raise Exception("You can't perform any task, you are not alive")
            
            if not round.is_night:
                raise Exception("It's not night yet")

            if round.player_role[player] != "doctor":
                raise Exception("You can't heal a player as you'r not a doctor")

            round.heal(player_to_heal)

            if round.is_night_ends:
                round.start_day()

            send_message(player, f"You are healing <@{player_to_heal}>")
        except Exception as e:
            send_message(player, text=str(e))

        return Response(status=status.HTTP_200_OK)

    
    @action(methods=['POST'], detail=False)
    def reveal(self, request, *args, **kwargs):
        payload = request.data
        print(json.dumps(payload, indent=2))

        try:
            round = Round.objects.get(team_id=payload["team_id"])
            player = payload["user_id"]
            player_to_reveal = payload["text"].split('|')[0].split('@')[1]

            if not round.player_is_alive[player]:
                raise Exception("You can't perform any task, you are not alive")
            
            if not round.is_night:
                raise Exception("It's not night yet")

            if round.player_role[player] != "sheriff":
                raise Exception("You can't reveal a player as you'r not a sheriff")

            role = round.reveal(player_to_reveal)

            if round.is_night_ends:
                round.start_day()

            send_message(player, f"<@{player_to_reveal}> is a {role}")
        except Exception as e:
            send_message(player, text=str(e))

        return Response(status=status.HTTP_200_OK)

    
    @action(methods=['POST'], detail=False)
    def vote(self, request, *args, **kwargs):
        payload = request.data
        print(json.dumps(payload, indent=2))

        try:
            round = Round.objects.get(team_id=payload["team_id"])
            player = payload["user_id"]
            player_to_vote = payload["text"].split('|')[0].split('@')[1]

            if round.is_night:
                raise Exception("It's not day yet")

            if not round.player_is_alive[player]:
                raise Exception("You can't perform any task, you are not alive")

            round.vote(player_to_vote)
            send_message(player, f"You voted for <@{player_to_vote}>")

            if round.is_voting_end:
                result = round.vote_result()
                if result:
                    send_message(os.getenv('CHANNEL'), f"<@{result}> is killed by townspeople")
                else:
                    send_message(os.getenv('CHANNEL'), "No one is killed by townspeople")

                winner = round.who_wins(result)
                if winner:
                    send_message(os.getenv('CHANNEL'), f"Game over!\n{winner} wins :tada:")
                    round.delete()
                else:
                    round.start_night()
            
        except Exception as e:
            send_message(player, text=str(e))

        return Response(status=status.HTTP_200_OK)
    
    
    @action(methods=['GET'],detail = False)
    def test(self, request, *args, **kwargs):


        return Response({"msg": "welcome to mafia moderator", "env": os.getenv('ENVIRONMENT'), "debug": settings.DEBUG}, status=status.HTTP_200_OK)