from django.conf import settings
from django.db import transaction

from rest_framework import viewsets, pagination, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.utils.notifications import email_update_notifier
from .models import UserProfile, UserVerifiedProfileCase
from .serializers import UserProfileSerializer, UserVerifiedProfileCaseSerializer
    

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
    

class UserProfileViewSet(viewsets.ModelViewSet):

    model = UserProfile
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = Pagination

    def get_queryset(self):
        
        return UserProfile.get_queryset(self.request.user)
    
    def get_object(self):
        try:
            user = self.request.user
            
            if user.is_superuser or user.is_staff:
                return UserProfile.objects.get(user_id=self.kwargs.get("pk"))

            if int(user.id) == int(self.kwargs.get("pk")):
                return UserProfile.objects.get(user_id=self.kwargs.get("pk"))
            
            return super().get_object()
        except Exception as e:
            return super().get_object()
        
    def list(self, request):

        if request.user.is_superuser or request.user.is_staff:
            queryset = UserProfile.objects.all()
        else:
            queryset = UserProfile.objects.filter(user=request.user)
        # queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, ))
    def find_recipient(self, request):

        from apps.app_payment_gateway.models import PaymentGateway
        from apps.app_payment_gateway.serializers import PaymentGatewaySerializer

        try:
            share_code = request.GET.get('share_code')
            profile = UserProfile.objects.get(share_code=share_code)
            payment_gateway = [PaymentGatewaySerializer(p, context={'request': request}).data for p in PaymentGateway.objects.all()]
            
            try:
                avatar = request.build_absolute_uri(profile.user.avatar.url)
            except:
                avatar = None

            return Response({'username': profile.user.get_full_name(), 'avatar':avatar, 'first_name': profile.user.first_name, 'last_name': profile.user.last_name, 'payment_gateway': payment_gateway, 'share_code': profile.share_code}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, ))
    def process_profiles(self, request):

        if request.user.is_superuser or request.user.is_staff:
            queryset = UserProfile.objects.filter(verified_details_status = UserProfile.VERIFIED_DETAILS_TYPE.Processing)
        else:
            queryset = UserProfile.objects.filter(verified_details_status = UserProfile.VERIFIED_DETAILS_TYPE.Processing, user=request.user)
        # queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
        
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, ))
    def verify_user_profile(self, request):

        try:
            
            id = request.data.get('user_id')
            details = request.data.get('details')
            complete = request.data.get('complete')
            share_code = request.data.get('share_code')
            
            if request.user.is_superuser or request.user.is_staff:

                with transaction.atomic():
                    user_profile = UserProfile.objects.get(user_id=id, share_code=share_code)
                    
                    try:
                        case = UserVerifiedProfileCase.objects.get(profile=user_profile, status=0)
                        
                        if complete == 'True' or complete == 'true':
                            case.details = 'Approved'
                            case.status = 1
                            case.save()

                            user_profile.verified_details = True
                            user_profile.verified_details_status = 2
                            user_profile.save()

                            #mail
                            email_update_notifier.delay(id, subject='Profile is verified', msg="Your profile is now verified. You can go ahead and use the services provided.", origin='UserProfileViewSet.verify_user_profile', sign_off='The Team', email_to=user_profile.user.email)
                            
                            #mail
                            email_update_notifier.delay(id, subject='Process profile: {}'.format(id), msg="Profile for user {}. {} has been verified by {}. {}".format(user_profile.user.id, user_profile.user.email, request.user.id, request.user.email), origin='UserProfileViewSet.verify_user_profile', sign_off='The Team', email_to=settings.EMAIL_HOST_USER, user_receiving_mail=1)
                        else:
                            case.details = details
                            case.save()
                            
                            user_profile.verified_details = False
                            user_profile.verified_details_status = 0
                            user_profile.save()

                            #mail
                            email_update_notifier.delay(id, subject='Profile needs some updates', msg="Please assure the follwing has been resolved before we can verify your profile:\n\n{}".format(details), origin='UserProfileViewSet.verify_user_profile', sign_off='The Team', email_to=user_profile.user.email)
                            
                            #mail
                            email_update_notifier.delay(id, subject='Process profile: {}'.format(id), msg="Profile for user {}. {} has been queried by {}. {} with the following:\n\n{}".format(user_profile.user.id, user_profile.user.email, request.user.id, request.user.email, details), origin='UserProfileViewSet.verify_user_profile', sign_off='The Team', email_to=settings.EMAIL_HOST_USER, user_receiving_mail=1)
                        
                        serializer = self.get_serializer(user_profile, context={'request': request})
                        
                        return Response(serializer.data, status=status.HTTP_200_OK)

                    except Exception as e:
                        
                        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                        
            else:
                return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class UserVerifiedProfileCaseViewSet(viewsets.ModelViewSet):

    model = UserVerifiedProfileCase
    serializer_class = UserVerifiedProfileCaseSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = Pagination

    def get_queryset(self):
        
        return UserVerifiedProfileCase.get_queryset(self.request.user)
    
    def get_object(self):
        try:
            user = self.request.user
            if user.is_superuser or user.is_staff:
                return UserVerifiedProfileCase.objects.get(profile__user_id=self.kwargs.get("pk"))

            if int(user.id) == int(self.kwargs.get("pk")):
                return UserVerifiedProfileCase.objects.get(profile__user_id=self.kwargs.get("pk"))
            
            return super().get_object()
        except:
            return super().get_object()
        
    def list(self, request):

        if request.user.is_superuser or request.user.is_staff:
            queryset = UserVerifiedProfileCase.objects.all()
        else:
            queryset = UserVerifiedProfileCase.objects.filter(profile__user=request.user)
        # queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)