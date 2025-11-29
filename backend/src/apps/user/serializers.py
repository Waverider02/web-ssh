from rest_framework import serializers
from .models import User
from apps.host.models import Host

class UserSerializer(serializers.ModelSerializer):
    sex = serializers.CharField(source='get_sex_display', read_only=True)
    password = serializers.CharField(write_only=True, required=False,allow_null=True,allow_blank=True,min_length=6)
    '''将id列表转换为host实例'''
    hosts = serializers.PrimaryKeyRelatedField(queryset=Host.objects.all(),many=True,required=False,)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'mobile', 'name', 'sex',
            'is_active', 'is_staff', 'is_superuser',
            'password', 'hosts',
        ]

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        '''员工无权提升权限'''
        if user and user.is_staff and not user.is_superuser:
            if attrs.get('is_staff') or attrs.get('is_superuser'):
                raise serializers.ValidationError('员工无权修改 staff 或 superuser 身份。')
        '''普通用户不能得到root主机'''
        if not attrs.get('is_staff') and not attrs.get('is_superuser'):
            hosts = attrs.get('hosts')
            if any(h.username == 'root' for h in hosts):
                raise serializers.ValidationError('普通用户不能关联主机名称为 root 的主机。')
        return super().validate(attrs)

    def validate_hosts(self, hosts):
        """
        专用字段校验：普通用户不能把 root 主机加进列表
        """
        user = self.context['request'].user
        # 只有普通用户才需要拦截
        if user and not user.is_staff and not user.is_superuser:
            # 只要列表里出现任何 name='root' 的主机就拒绝
            if any(h.name == 'root' for h in hosts):
                raise serializers.ValidationError('普通用户不能关联主机名称为 root 的主机。')
        return hosts

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance