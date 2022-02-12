from rest_framework import routers
from api.viewsets import SlackAppViewset
from django.urls import path, include

router = routers.DefaultRouter()

router.register('', SlackAppViewset, basename='slack')

urlpatterns = [
    path('', include(router.urls))
]