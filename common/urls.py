from django.urls import path, include

from .views import RegisterAPIView, LoginAPIView, UserAPIView, LogoutAPIView, UserInfoAPIView, UserPasswordAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('users/info', UserInfoAPIView.as_view()),
    path('users/password', UserPasswordAPIView.as_view())
]