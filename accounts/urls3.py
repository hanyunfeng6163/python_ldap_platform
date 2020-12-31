from django.urls import path

from accounts.user import user_profile, change_password

urlpatterns = [
    path('user_profile/', user_profile, name='user_profile'),
    path('change_password/', change_password, name='change_password'),
]