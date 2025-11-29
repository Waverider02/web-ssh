from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # 先让 DRF 做默认处理
    response = exception_handler(exc, context)

    # 统一包装返回格式
    if response is not None:
        return Response({
            'code': response.status_code,
            'message': response.data.get('detail', str(exc)),
            'data': None
        }, status=response.status_code)

    # DRF 没处理的异常（如 Django 原生 500）
    return Response({
        'code': 500,
        'message': '服务器内部错误',
        'data': None
    }, status=500)