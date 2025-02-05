from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from .models import URL,ImageMetadata
from .serializers import URLSerializer 
from django_filters.rest_framework import DjangoFilterBackend
from .filters import URLFilter

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home(request):
    return render(request, "index.html")

class URLViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','options']
    queryset=URL.objects.all()
    serializer_class=URLSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = URLFilter  