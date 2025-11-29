from rest_framework.routers import DefaultRouter
from .views import HostViewSet,HostCategoryViewSet,HostFileAPIView,UploadFileAPIView,DownloadFileAPIView
from django.urls import path

router = DefaultRouter()
router.register(r'hosts', HostViewSet, basename='host')
router.register(r'category', HostCategoryViewSet, basename='category')

urlpatterns = router.urls + [
    path('<int:dev_id>/file/', HostFileAPIView.as_view(), name='file'),
    path('<int:dev_id>/upload/', UploadFileAPIView.as_view(), name='upload'),
    path('<int:dev_id>/download/', DownloadFileAPIView.as_view(), name='download'),
]
