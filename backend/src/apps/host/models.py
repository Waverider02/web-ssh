from django.db import models

class HostCategory(models.Model):
    name = models.CharField('类别名称', max_length=50, unique=True,error_messages={'unique': '该主机分类已存在'})

    class Meta:
        db_table = 'host_category'
        verbose_name = '主机分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Host(models.Model):
    STATUS_CHOICES = [(1, '在线'), (0, '离线')]
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=0)
    category = models.ForeignKey(HostCategory, on_delete=models.CASCADE, verbose_name='类别')
    name = models.CharField('主机名称', unique=True, max_length=100,error_messages={'unique': '该主机名称已存在'})
    username = models.CharField('登录账户', max_length=50)
    ip_addr = models.GenericIPAddressField('IP地址')
    port = models.IntegerField('端口', default=22)
    connect_pwd = models.CharField('连接密码', max_length=255)
    remark = models.TextField('备注', blank=True)
    '''SSH服务器的公钥与私钥'''
    public_key = models.TextField(blank=True)
    private_key = models.TextField(blank=True)

    class Meta:
        db_table = 'host'
        verbose_name = '主机'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}({self.ip_addr}:{self.port})"