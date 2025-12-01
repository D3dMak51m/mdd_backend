# apps/users/views.py
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserRegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import FCMTokenUpdateSerializer
from drf_yasg.utils import swagger_auto_schema

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

class FCMTokenUpdateView(generics.UpdateAPIView):
    """
    Эндпоинт для обновления FCM-токена текущего пользователя.
    """
    serializer_class = FCMTokenUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Возвращаем текущего пользователя
        return self.request.user

    @swagger_auto_schema(
        tags=['Auth'],
        operation_summary="Обновление FCM токена",
        operation_description="Сохраняет FCM токен устройства для текущего пользователя."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)  # Скрываем PUT, так как используем PATCH
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class CustomLoginView(TokenObtainPairView):
    """
    Вход в систему. Возвращает токены и данные пользователя.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_summary="Вход в систему (Login)",
        operation_description="Возвращает Access/Refresh токены и информацию о пользователе.",
        responses={
            200: CustomTokenObtainPairSerializer,
            401: "Неверные учетные данные"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)