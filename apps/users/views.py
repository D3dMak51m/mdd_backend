# apps/users/views.py
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Представление для регистрации новых пользователей.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем токены для нового пользователя
        refresh = RefreshToken.for_user(user)

        # Сериализуем данные пользователя для ответа
        user_data = UserSerializer(user).data

        return Response({
            "user": user_data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=['Auth'],
        operation_summary="Регистрация нового пользователя",
        operation_description="Создает нового пользователя и возвращает пару access/refresh токенов."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)