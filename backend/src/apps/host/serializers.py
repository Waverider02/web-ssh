from rest_framework import serializers
from .models import Host, HostCategory
from utils.ssh import generate_key_pair,push_public_key,probe_ssh_connect

class HostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HostCategory
        fields = ['id', 'name']


class HostSerializer(serializers.ModelSerializer):
    # 只读字段：前端表格 category_name
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Host
        fields = [
            'id', 'status', 'category', 'category_name',
            'name', 'username', 'ip_addr', 'port',
            'connect_pwd', 'remark',
        ]
        extra_kwargs = {
            'category': {'write_only': False},  # 写时用 id，读时都读
        }

    def validate(self, attrs):
        """创建/更新都会先走到这里"""
        # 取待验证的连接信息
        host = attrs.get('ip_addr', getattr(self.instance, 'ip_addr', None))
        port = attrs.get('port',   getattr(self.instance, 'port',   None))
        user = attrs.get('username', getattr(self.instance, 'username', None))
        pwd  = attrs.get('connect_pwd')   # 仅临时用

        if not host or not port or not user:
            raise serializers.ValidationError('连接信息 (IP/端口/用户名) 不完整')

        # 探测
        err = probe_ssh_connect(host, port, user, password=pwd)
        if err:
            raise serializers.ValidationError({'password': f'连接失败：{err}'})
        
        # 先判断对应连接是否已注册私钥
        instance = Host.objects.filter(ip_addr = host,port = int(port),username = user).first()

        if(not instance):
            # 生成密钥
            print("生成密钥中...")
            private, public = generate_key_pair()
            attrs['private_key'] = private
            attrs['public_key']  = public
            # 把公钥推到远端
            push_public_key(attrs)
        else:
            # 如果已经注册,则直接赋值
            print("该连接链接已经注册")
            attrs['private_key'] = instance.private_key
            attrs['public_key']  = instance.public_key
        return attrs
