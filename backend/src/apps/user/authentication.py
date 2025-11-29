from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class MobileOrUsernameBackend(ModelBackend):
    """
    允许用手机号或用户名+密码登录
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # username 字段可能是手机号也可能是昵称
        user = User.objects.filter(
            Q(mobile=username) | Q(username=username)
        ).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
