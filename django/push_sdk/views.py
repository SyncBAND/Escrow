from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import MultipleObjectsReturned

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import PushDevice
from .serializers import PushDeviceSerializer

from apps.utils.permissions import IsOwnerProfileOrReadOnly

class Pagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'paginator': {'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
                'count': self.page.paginator.count,
                'page_number': self.page.number,
                'num_pages': self.page.paginator.num_pages,
            },
            'results': data
        })
        

class PushDeviceViewSet(viewsets.ModelViewSet):

    model = PushDevice
    serializer_class = PushDeviceSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination

    def get_queryset(self):
        
        if self.request.user.is_superuser:
            return PushDevice.objects.all(active=True)
        else:
            return PushDevice.objects.filter(active=True, user=self.request.user)

        return PushDevice.objects.none()