from rest_framework import viewsets,status
from .models import Host,HostCategory
from .serializers import HostSerializer,HostCategorySerializer
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.ssh import exec_cmd,upload_file,download_file
from utils.permissions import IsSuperUser,IsStaff,IsActie,IsActieReadOnly

class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all().select_related('category')
    serializer_class = HostSerializer
    permission_classes = [IsSuperUser|IsStaff|IsActieReadOnly]

class HostCategoryViewSet(viewsets.ModelViewSet):
    queryset = HostCategory.objects.all()
    serializer_class = HostCategorySerializer
    permission_classes = [IsSuperUser|IsStaff|IsActieReadOnly]

class HostFileAPIView(APIView):
    '''
    POST /host/<dev_id>/file?path=<base_path>
    Body:{"cmd":"pwd","args",[]}
    '''
    ALLOW_CMD = {'pwd','ls','rm','mkdir'}
    permission_classes = [IsActie]

    def post(self,request,dev_id):
        # 1. 查询参数
        base_path = request.query_params.get('path','')
        # 2. 获取JSON参数
        cmd = request.data.get('cmd','pwd')
        args = request.data.get('args',[])
        # 3. 安全校验
        if cmd not in self.ALLOW_CMD:
            return Response({'code':2,'msg':'forbidden cmd'},status=status.HTTP_403_FORBIDDEN)
        cmd = f'cd {base_path} && {cmd} '+' '.join(args)
        # 4. 执行
        try:
            host_info = Host.objects.filter(pk=dev_id).values().first()
            print(f'cmd:{cmd}')
            out = exec_cmd(host_info=host_info,cmd=cmd)
            print(f'out:{out}')
            return Response({'code': 0, 'msg': out})
        except Exception as e:
            return Response({'code': 4, 'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadFileAPIView(APIView):

    permission_classes = [IsActie]

    def post(self, request,dev_id):
        # 1. 查询参数
        base_path = request.query_params.get('path','')
        # 2. 获取JSON参数
        file_name = request.data.get('filename','nonename')
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'code': 1, 'msg': '缺少文件'})
        try:
        # 3. 连接SSH上传文件
            host_info = Host.objects.filter(pk=dev_id).values().first()
            upload_file(host_info,file_obj,base_path,file_name)
            return Response({'code': 0, 'msg': '文件已上传', 'path': base_path,'name':file_name})
        except Exception as e:
            return Response({'code': 2, 'msg': str(e)})

class DownloadFileAPIView(APIView):

    permission_classes = [IsActie]

    def post(self, request,dev_id):
        # 1. 查询参数
        base_path = request.query_params.get('path','')
        # 2. 获取JSON参数
        file_name = request.data.get('filename','nonename')
        # 3. 返回文件对象
        try:
            host_info = Host.objects.filter(pk=dev_id).values().first()
            file,file_size = download_file(host_info,base_path,file_name)
            response = FileResponse(file,as_attachment=True,filename=str(file_name))
            response['Content-Length'] = file_size
            return response
        except Exception as e:
            return Response({'code': 2, 'msg': str(e)})
    
