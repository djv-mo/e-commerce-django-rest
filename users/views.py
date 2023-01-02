from rest_framework import generics
from .serializers import UserSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        password = self.request.data.get('password')
        validate_password(password)  # check password strength
        serializer.save()


class ProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
