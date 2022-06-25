from django.utils import timezone

from rest_framework import status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Message
from .serializers import MessageSerializer
from push_sdk.models import PushDevice

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


class MessageViewSet(viewsets.ModelViewSet):

    model = Message
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination

    def get_queryset(self):
        
        if self.request.user.is_superuser:
            return Message.objects.all().order_by('-modified')
        else:
            return Message.objects.filter(user=self.request.user).order_by('-modified')
    

    @decorators.action(detail=False, methods=['patch'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def delivered(self, request):
        
        try:
            api_message_id = request.data.get('api_message_id')

            message = Message.objects.get(id=api_message_id)

            message.status = Message.TYPE.MESSAGE_DELIVERED

            try:
                device = PushDevice.objects.select_related().filter(user=request.user, active=True).update(resend_counter = 0)
                message.logs = "{}\n\n{} - device counter reset successful".format(message.logs, timezone.localtime(timezone.now()))
            except Exception as e:
                message.logs = "{}\n\n{} - device error: {}".format(message.logs, timezone.localtime(timezone.now()), e)

            message.save()

            return Response({'detail': 'Updated'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': 'No id'}, status=status.HTTP_200_OK)

        