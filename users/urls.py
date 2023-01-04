from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name='register'),
    path('me/', views.ProfileView.as_view(), name='profile'),
]
