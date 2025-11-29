from django.http import FileResponse,StreamingHttpResponse
import logging
import time

# 自定义logger,用于http访问信息记录
http_logger = logging.getLogger("http.access") 

# Http访问日志中间件
class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        t0 = time.time()
        response = self.get_response(request)
        cost = int((time.time() - t0) * 1000)

        # 取真实 IP
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR", "-")

        if isinstance(response, (FileResponse, StreamingHttpResponse)):
            length = response.get('Content-Length') or 0
        else:
            length = len(response.content)

        # 拼接成一条日志
        msg = f'{ip} | "{request.method} {request.get_full_path()} HTTP/1.1" {response.status_code} {length} {cost}ms'
        http_logger.info(msg)
        return response