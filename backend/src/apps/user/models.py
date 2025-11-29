from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
import re

def mobile_validate(value: str):
    if not re.fullmatch(r'^1[3-9]\d{9}$', value):
        raise ValidationError('手机号格式不正确')

class SexChoices(models.IntegerChoices):
    MALE = 1, '男'
    FEMALE = 2, '女'
    UNKNOWN = 0, '未知'

class User(AbstractUser):
    email = models.EmailField('邮箱', blank=True, null=True)
    first_name = models.CharField('first name', max_length=30, blank=True, null=True)
    last_name = models.CharField('last name', max_length=30, blank=True, null=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    last_login = models.DateTimeField('last login', blank=True, null=True)
    # 以下为前端需要的字段信息
    username = models.CharField('用户名',max_length=30,unique=True,error_messages={'unique': '该用户名已存在'})
    mobile = models.CharField('手机号',max_length=11,unique=True,validators=[mobile_validate],error_messages={'unique': '该手机号已注册'})
    name = models.CharField('真实姓名', max_length=20, blank=True)
    sex = models.IntegerField('性别', choices=SexChoices.choices, default=SexChoices.UNKNOWN)
    # 权限三件套（AbstractUser 已带，这里仅为了文档/序列化可见）
    is_active = models.BooleanField('有效', default=True)
    is_staff = models.BooleanField('管理员', default=False)
    is_superuser = models.BooleanField('超级管理员', default=False)
    hosts = models.ManyToManyField('host.Host', verbose_name='关联主机', blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'

    def __str__(self):
        return f'{self.username}:({self.mobile})'