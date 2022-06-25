from django.contrib.contenttypes.models import ContentType

from rest_framework import status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Support, SupportActivity, SupportRatings, SupportRatingsHistory
from .serializers import SupportSerializer, SupportActivitySerializer
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.user_profile.models import UserProfile
from apps.chat.models import Chat, ChatList
from apps.chat.serializers import ChatListSerializer
from apps.utils.notifications import email_notifier

from django.db import transaction


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
 

class SupportViewSet(viewsets.ModelViewSet):

    model = Support
    serializer_class = SupportSerializer
    pagination_class = Pagination

    permission_classes = (IsAuthenticated, )
    
    def list(self, request):

        if request.user.is_superuser:
            queryset = Support.objects.all()
        else:
            queryset = Support.objects.filter(user=request.user)
    
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def processing(self, request):
        # superuser, 

        if request.user.is_superuser:
            queryset = Support.objects.get(status=Support.STATUS_TYPE.Processing).order_by('-modified')
        else:
            queryset = Support.objects.filter(status=Support.STATUS_TYPE.Processing, user=request.user).order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def cancelled(self, request):

        if request.user.is_superuser:
            queryset = Support.objects.get(status=Support.STATUS_TYPE.Cancelled).order_by('-modified')
        else:
            queryset = Support.objects.filter(status=Support.STATUS_TYPE.Cancelled, user=request.user).order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def attended(self, request):

        if request.user.is_superuser:
            queryset = Support.objects.get(status=Support.STATUS_TYPE.Attended).order_by('-modified')
        else:
            queryset = Support.objects.filter(status=Support.STATUS_TYPE.Attended, user=request.user).order_by('-modified')
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Chats: 
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def chatlist(self, request):

        id = request.GET.get('id', 0)
        
        queryset = []
        try:
            
            content_type = ContentType.objects.get_for_model(Support)
            if request.user.is_superuser:
                queryset = ChatList.objects.filter(content_type=content_type, object_id=id, respondent=request.user).order_by('-modified')

                with transaction.atomic():
                    if not queryset.exists():
                        try:
                            message = "Hi. My name is, "+str(request.user.first_name)+". I'll be your assistant."
                            support = Support.objects.get(id=id)
                            chatlist = support.chat.create(creator=support.user, respondent=request.user, last_message_sent_by=request.user.id, last_message=message, creator_unread=1)
                            Chat.objects.create(chat_list=chatlist, message=message, sent_by=request.user)
                            queryset = [chatlist]

                            email_notifier.delay(support.user.id, origin="SupportViewSet.chatlist", message=message, subject="Support: {}. {}".format(support.id, support.title), email_to=[support.user.email])
                        except:
                            pass

            else:
                queryset = ChatList.objects.filter(content_type=content_type, object_id=id, creator=request.user).order_by('-modified')
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ChatListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ChatListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def rate(self, request, pk=0):
        
        try:
            rating = request.data.get('rating', None)
            review = request.data.get('review', '')
            
            if rating is None or rating == 0:
                return Response({'detail': 'Rating was not given'}, status=status.HTTP_400_BAD_REQUEST)

            rating = int(rating)
            
            with transaction.atomic():

                support_being_rated = Support.objects.select_related().get(pk = pk)

                user_profile_making_rating = UserProfile.objects.select_related().get(user = request.user)
                
                try:
                    support_ratings = SupportRatings.objects.get(user_profile_making_rating=user_profile_making_rating, support_being_rated=support_being_rated)
                    
                    SupportRatingsHistory.objects.create(support_ratings=support_ratings, previous_rating=support_ratings.rating, previous_review=support_ratings.review)
                    
                    # if editting, minus previous rating and add new one
                    # to get rating percentage = (support_being_rated.total_sum_of_ratings/5)/support_being_rated.total_number_of_ratings
                    support_being_rated.total_sum_of_ratings = support_being_rated.total_sum_of_ratings - support_ratings.rating + rating
                    support_being_rated.save()

                    support_ratings.review = review
                    support_ratings.rating = rating
                    support_ratings.editted = True
                    support_ratings.save()

                except:

                    SupportRatings.objects.create(user_profile_making_rating=user_profile_making_rating, support_being_rated=support_being_rated, review=review, rating=rating)
                    
                    # to get rating percentage = (support_being_rated.total_sum_of_ratings/5)/support_being_rated.total_number_of_ratings
                    support_being_rated.total_sum_of_ratings = support_being_rated.total_sum_of_ratings + rating
                    support_being_rated.total_number_of_ratings = support_being_rated.total_number_of_ratings + 1
                    support_being_rated.save()
                
                return Response({'detail': 'Rated'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            
class SupportActivityViewSet(viewsets.ModelViewSet):

    model = SupportActivity
    serializer_class = SupportActivitySerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated, )
    
    def list(self, request):

        support_id = request.GET.get('support_id', request.data.get('support_id', 0))

        if request.user.is_superuser:
            queryset = SupportActivity.objects.all()
        else:
            queryset = SupportActivity.objects.filter(support_id=support_id, user=request.user)
    
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
