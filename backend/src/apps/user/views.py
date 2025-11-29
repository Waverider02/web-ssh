from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from utils.permissions import IsSuperUser,IsStaff,IsActieReadOnly

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    纯 ModelViewSet: list / create / retrieve / update / destroy 自动实现
    额外 action: 批量删除 / 重置密码
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser|IsStaff|IsActieReadOnly]

