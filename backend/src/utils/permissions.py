from rest_framework.permissions import BasePermission,SAFE_METHODS
from django.contrib.auth import get_user_model

User = get_user_model()

class IsSuperUser(BasePermission):
    message = '超级管理员可以操作任何数据'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
            request.user.is_superuser and request.user.is_active

class IsStaff(BasePermission):
    message = '员工只能操作普通用户'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
            request.user.is_staff and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if view.queryset.model is not User:
            return True
        elif obj.is_superuser or obj.is_staff:
            return False
        return True

class IsActie(BasePermission):
    message = '激活员工可操作'
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
            request.user.is_active

class IsActieReadOnly(BasePermission):
    message = '激活员工只读'
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated and \
                request.user.is_active
        return False
