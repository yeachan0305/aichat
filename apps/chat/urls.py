from django.urls import path, re_path
from apps.chat import views

app_name = 'chat'

urlpatterns = [
    # path('', views.chat, name='chat'),  # '/chat/' URL에 대해 chat 뷰 처리

    # chat_id를 URL에서 받아오는 패턴
    re_path(r'^(?P<user_id>\d+)/(?P<bot_id>\d+)(?:/(?P<chat_id>\d+))?$', views.chat, name='chat'),
    # 채팅 삭제
    path("delete/", views.delete_chat, name="delete_chat"),
]   