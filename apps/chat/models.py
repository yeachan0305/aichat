from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Chats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    title = models.CharField(max_length=255, default="New Chat")  # 사이드바에 표시될 제목
    bot_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='messages')
    user = models.TextField()  # 'user'가 입력한 메세지
    assistant = models.TextField() # 'assistant'가 입력한 메세지
    timestamp = models.DateTimeField(auto_now_add=True)