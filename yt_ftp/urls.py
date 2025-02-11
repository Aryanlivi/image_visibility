from django.urls import path, include
from rest_framework_nested import routers
from . import views
router = routers.DefaultRouter()
router.register('/urls',views.URLViewSet,basename="urls")
router.register('/ftp_configs',views.FTPConfigViewSet,basename="ftp_configs")


urlpatterns = [
    path("/", views.home, name="home"),
    path('/api', include(router.urls)),
]