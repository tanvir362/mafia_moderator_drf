from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from slack_sdk import WebClient
import os
from django.conf import settings




class SlackAppViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes=[AllowAny]

    def get_serializer_class(self, *args, **kwargs):
        pass
    
    @action(methods=['POST'],detail = False)
    def new_round(self, request, *args, **kwargs):
        data = request.data
        # print(data)

        client = WebClient(token=os.getenv('BOT_AUTH_TOKEN'))
        client.chat_postEphemeral(
            channel=os.getenv('CHANNEL'),
            text="Hello from your app! :tada:",
            user=""
        )
        
        return Response(data, status=status.HTTP_200_OK)


    @action(methods=['GET'],detail = False)
    def test(self, request, *args, **kwargs):


        return Response({"msg": "welcome to mafia moderator", "env": os.getenv('ENVIRONMENT'), "debug": settings.DEBUG}, status=status.HTTP_200_OK)