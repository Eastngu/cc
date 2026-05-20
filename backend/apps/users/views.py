from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsBoss
from .serializers import LoginSerializer, UserCreateSerializer, UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            if '用户名或密码错误' in str(serializer.errors):
                return Response(
                    {'detail': '用户名或密码错误'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({'detail': '请提供旧密码和新密码'}, status=400)
        if not request.user.check_password(old_password):
            return Response({'detail': '旧密码错误'}, status=400)
        if len(new_password) < 6:
            return Response({'detail': '新密码长度不能少于6位'}, status=400)
        request.user.set_password(new_password)
        request.user.save()
        return Response({'detail': '密码修改成功'})


class UserViewSet(viewsets.ModelViewSet):
    """User CRUD - only boss can access"""
    queryset = User.objects.all()
    permission_classes = [IsBoss]
    search_fields = ['username', 'real_name', 'phone']
    filterset_fields = ['role', 'is_active']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        user = self.get_object()
        password = request.data.get('password')
        if not password:
            return Response({'detail': '请提供新密码'}, status=400)
        user.set_password(password)
        user.save()
        return Response({'detail': '密码重置成功'})
