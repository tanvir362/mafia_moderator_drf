from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
import os
from django.conf import settings
from api.models import Round
from api.services import send_message


class SlackAppViewset(viewsets.ReadOnlyModelViewSet):
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
                text="Now round started.\nEveryone, please run /my_role command to get your role"
            )
        
        return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'],detail = False)
    def test(self, request, *args, **kwargs):


        return Response({"msg": "welcome to mafia moderator", "env": os.getenv('ENVIRONMENT'), "debug": settings.DEBUG}, status=status.HTTP_200_OK)