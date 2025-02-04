from django_filters.rest_framework import FilterSet,CharFilter
from .models import URL
from django.db import models


class URLFilter(FilterSet):
    class Meta:
        model = URL
        fields={
        "name": ["icontains"],
    }