from .base import *
from datetime import timedelta

# 应用程序
INSTALLED_APPS = [
    'daphne',
    'channels',
] + INSTALLED_APPS + [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',         
    'apps.host',
    'apps.user',
]

# 异步
ASGI_APPLICATION = 'apps.asgi.application'

# 通道层：开发阶段用内存或者Redis
'''
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
'''

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://:12345678@127.0.0.1:6379/0"],   # 默认库 0
            # 如果 Redis 没有密码
            # "hosts": ["redis://127.0.0.1:6379/1"],
            # 或者哨兵/集群
            # "hosts": [{"host": "127.0.0.1", "port": 6379, "db": 0, "password": "12345678"}],
            "capacity": 1500,      # 单通道最大消息积压
            "expiry": 10,          # 消息过期秒数
        },
    }
}


# 中间件
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE + ["utils.middleware.AccessLogMiddleware"]

# 自定义用户模型
AUTH_USER_MODEL = 'user.User'

# 登录认证方式
AUTHENTICATION_BACKENDS = [
    'apps.user.authentication.MobileOrUsernameBackend',  # 自定义
    'django.contrib.auth.backends.ModelBackend',          # 默认兜底
]

# DRF
REST_FRAMEWORK = {
    # 1. 渲染器：浏览器 vs JSON
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',   # 开发阶段可保留
    ],

    # 2. 解析器：允许客户端上传哪些格式
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],

    # 3. 认证方式：Session、Token、JWT 可并存
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',  # 需要 django-rest-auth
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # 若用 simple-jwt
    ],

    # 4. 权限策略：全局默认“登录后可用”
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    # 5. 频率限流：匿名/用户 分别控制
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/min',   # 匿名 IP
        'user': '100/min',  # 已登录用户
    },

    # # 6. 分页：统一返回 response.data:{count/next/previous/results} 结构
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 20,

    # 7. 异常处理：自定义报错格式
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',

    # 8. 过滤/排序/搜索后端
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # 9. 接口文档：drf-yasg 需要 AllowAny 才能免登录看文档
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',

}

# JWT认证
SIMPLE_JWT = {
    # ---------- 基础 ----------
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),   # 访问令牌
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # 刷新令牌
    'AUTH_HEADER_TYPES': ('Bearer',),                # 请求头前缀
    'ALGORITHM': 'HS256',                            # 对称算法（默认）
    'SIGNING_KEY': SECRET_KEY,                       # 使用 Django 全局密钥

    # ---------- 高级（可选） ----------
    'ROTATE_REFRESH_TOKENS': True,   # 刷新时颁发新 refresh_token
    'BLACKLIST_AFTER_ROTATION': True,  # 旧 refresh 加入黑名单（需上表 blacklist 应用）
    'UPDATE_LAST_LOGIN': True,         # 刷新时更新 user.last_login

    # 自定义用户模型字段映射（无 username 场景）
    'USER_ID_FIELD': 'id',             # 模型里唯一标识字段
    'USER_ID_CLAIM': 'user_id',        # JWT payload 中对应的 key

    # 严格声明校验（生产推荐）
    'REQUIRED_CLAIMS': ['exp', 'iat', 'jti', 'user_id'],

    'UPDATE_LAST_LOGIN': True,          # 自动更新最后登录时间

    # 滑动窗口续期（可选）
    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# 数据库
DATABASES = {
    'default': {
        # 1. 驱动
        'ENGINE': 'django.db.backends.mysql',

        # 2. 基本连接
        'NAME': os.getenv('DB_NAME', 'web-ssh'),          # 提前 CREATE DATABASE
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', '12345678'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),

        # 3. 连接池（Django 3.2+ 支持 CONN_MAX_AGE）
        'CONN_MAX_AGE': 600,                      # 秒：复用连接 10 min
        'CONN_HEALTH_CHECKS': True,               # Django 5.0+ 心跳检测

        # 4. 客户端选项
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET "
                            "sql_mode='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION', "
                            "time_zone='+00:00'",   # UTC 时区，与 Django USE_TZ 一致
            'isolation_level': 'read committed',   # 避免脏读
        },
    }
}

# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 处理器
    'handlers': {
        # HTTP 访问日志（INFO 级，每天一切）
        'http_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'http.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,        # 保留 30 份
            'formatter': 'access',
        },
        # 错误日志（ERROR 级，最大10MB）
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    # 日志器
    'loggers': {
        # Django 内置 HTTP 请求/响应日志
        'http.access': {
            'handlers': ['http_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {  # 404/500 等
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 兜底：项目代码里 logger.error() 也会进 error.log
        '': {  # root logger
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
        },
    },
    # 格式化器
    'formatters': {
        'verbose': {
            'format': '{asctime} | {levelname} | {name}:{lineno} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'access': {
            'format': '{asctime} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
}


# CORS跨域
# 白名单：允许哪些源跨域调用
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # 前端Vite 地址
    "http://127.0.0.1:5173",
]

# 允许携带 cookie / authorization 头
CORS_ALLOW_CREDENTIALS = True

# 允许的请求方法 & 头（默认已包含常用，可按需追加）
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]

# 开发偷懒模式（全部放行）
CORS_ALLOW_ALL_ORIGINS = True
