from django_filters.rest_framework import FilterSet,CharFilter
from .models import URL,FTPConfig
from django.db import models


class URLFilter(FilterSet):
    class Meta:
        model = URL
        fields={
        "name": ["icontains"],
    }
        

class FTPConfigFilter(FilterSet):
    class Meta:
        model = FTPConfig
        fields={
        "ftp_server": ["icontains"],
    }
        
