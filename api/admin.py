import imp
from django.contrib import admin
from api.models import Round

# Register your models here.
@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ['id', 'team_id', 'channel_id', 'is_night']
