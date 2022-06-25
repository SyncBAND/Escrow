from django.shortcuts import render, get_object_or_404

from rest_framework import status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Chat, ChatList
from .serializers import ChatSerializer, ChatListSerializer
from apps.utils.permissions import IsOwnerProfileOrReadOnly

from django.contrib.auth import get_user_model


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


class ChatListViewSet(viewsets.ModelViewSet):

    model = ChatList
    serializer_class = ChatListSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination
    
    def list(self, request):
        
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        id = self.request.GET.get('id', '0')
        model = self.request.GET.get('model', 'Enquiry')

        if self.request.user.is_superuser:
            return ChatList.objects.filter(id=id).order_by('-modified')
        else:
            # currently not in use - refer to models using Chatlst as GenericRelation
            return ChatList.objects.filter(id=id, creator_id=self.request.user.id, active_creator=True).order_by('-modified')
                

    @decorators.action(detail=False, methods=['put'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def delete(self, request):
        
        if self.request.user.is_superuser:
            ChatList.objects.filter(id=id).update(status=ChatList.TYPE.Deleted)
        else:
            return ChatList.objects.filter(id=id, creator_id=request.user.id, active_creator=True).update(active_creator=False)

        return Response({'detail': 'Chat deleted'}, status=status.HTTP_200_OK)


class ChatViewSet(viewsets.ModelViewSet):

    model = Chat
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination
    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset.order_by('-created'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):

        chat_list_id = self.request.GET.get('chat_list_id', 0)

        if self.request.user.is_superuser:
            return Chat.objects.filter(chat_list_id=chat_list_id)
        else:
            return Chat.objects.filter(chat_list_id=chat_list_id, chat_list__creator_id=self.request.user.id, active_creator=True)
                
        return []

    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def chats(self, request):

        # fix in future not to pull everything - but to paginate

        if request.user.is_superuser:
            chat_list_id = self.request.GET.get('id', 0)
            queryset = Chat.objects.filter(chat_list_id=chat_list_id)
        else:
            return Response({'detail': 'Not permitted'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @decorators.action(detail=False, methods=['put'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def delete(self, request):

        id = request.data.get('id', 0)
        
        if self.request.user.is_superuser:
            Chat.objects.filter(id=id)
        else:
            return Chat.objects.filter(id=id, chat_list__creator_id=request.user.id, active_creator=True).update(active_creator=False)

        return Response({'detail': 'Message deleted'}, status=status.HTTP_200_OK)

