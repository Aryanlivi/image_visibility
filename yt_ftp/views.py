from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from .models import URL,ImageMetadata
from .serializers import URLSerializer 
# Create your views here.

class URLViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','head','options']
    queryset=URL.objects.all()
    serializer_class=URLSerializer