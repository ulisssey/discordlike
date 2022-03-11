from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('room/<int:pk>/', room, name='room'),
    path('create_room/', createroom, name='create'),
    path('update_room/<str:pk>', updateroom, name='update'),
    path('delete_room/<str:pk>', deleteroom, name='delete'),
    path('delete_message/<str:pk>', deletemessage, name='delete_message'),
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_page, name='register'),
    path('profile/<str:pk>', userprofile, name='profile'),
    path('update-user/', updateuser, name='update-user'),
    path('topics/', topicspage, name='topics'),
    path('activity/', activitypage, name='activity'),
]