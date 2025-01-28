from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('urls',views.URLViewSet,basename="urls")




urlpatterns = [
    path('/', include(router.urls)),
]