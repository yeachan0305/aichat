from django.contrib import admin
from .models import Chats, Message

# Register your models here.
admin.site.register(Chats)
admin.site.register(Message)