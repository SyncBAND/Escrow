from rest_framework import viewsets, pagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import PaymentGateway, PaymentChargeFee
from .serializers import PaymentGatewaySerializer, PaymentChargeFeeSerializer


class Pagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size = 5

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
 

class PaymentGatewayViewSet(viewsets.ModelViewSet):

    model = PaymentGateway
    serializer_class = PaymentGatewaySerializer
    pagination_class = Pagination

    permission_classes = (IsAuthenticated, )
    
    def list(self, request):

        if request.user.is_authenticated:
            queryset = PaymentGateway.objects.all()
        else:
            queryset = PaymentGateway.objects.none()
    
        page = self.paginate_queryset(queryset.only('id').order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.only('id').order_by('-modified'), many=True)
        return Response(serializer.data)

        
class PaymentChargeFeeViewSet(viewsets.ModelViewSet):

    model = PaymentChargeFee
    serializer_class = PaymentChargeFeeSerializer
    pagination_class = Pagination

    authentication_classes = ()
    permission_classes = (AllowAny, )
    
    def list(self, request):

        queryset = PaymentChargeFee.get_queryset()
        page = self.paginate_queryset(queryset.order_by('id'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('id'), many=True)
        return Response(serializer.data)