from django.urls import path
from apps.bot import views
from .models import bots

app_name = 'bot'

urlpatterns = [
    path('lists/', views.lists),
    path('create_bot/', views.create),
    path('lists/category/<int:category_id>/', views.lists, name='bot_list'),
]