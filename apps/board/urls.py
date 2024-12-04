from django.conf import settings
from django.urls import path, include
from apps.board import views 

app_name = 'board'

urlpatterns = [
    path('', views.index),
    path('write/', views.write),
    path('read/<id>/', views.read),
    path('delete/', views.delete),
    path('update/<id>/', views.update),
    path('<int:post_id>/like/', views.like_post, name='like_post'),
    path('category/<int:category_id>/', views.index, name='post_list'),
] 