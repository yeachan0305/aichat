from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views

from apps.users import views 

app_name = 'users'

urlpatterns = [
    path('join/', views.join),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]