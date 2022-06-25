from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
 
from rest_framework import decorators, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UpdateUserSerializer
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.user_profile.models import UserProfile
from apps.utils.notifications import mail_notifier, email_update_notifier, email_notifier


class UserViewSet(viewsets.ModelViewSet):

    model = get_user_model()
    serializer_class = UpdateUserSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return get_user_model().objects.filter(pk=self.kwargs['pk'])
        return get_user_model().objects.none()
    
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def email(self, request):
        
        if request.user.is_superuser:
            try:
                user = get_user_model().objects.get(id=request.data['user_id'])
                
                message = str(request.data['message'])

                email_notifier.delay(user.id, get_current_site(request).domain, origin="apps.user_profile.api.UserViewSet.email", message=message, subject=request.data['subject'], email_to=[user.email])

                return Response({'detail': "Email was sent."}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)


class DeleteUserViewSet(viewsets.ModelViewSet):

    model = get_user_model()
    permission_classes = [IsAuthenticated, IsOwnerProfileOrReadOnly]
    serializer_class = UpdateUserSerializer
    
    def get_queryset(self):
        if 'pk' in self.kwargs:
            return get_user_model().objects.filter(pk=self.kwargs['pk'])
        return get_user_model().objects.none()

class ChangePasswordViewSet(APIView):

    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)

    def patch(self, request, pk=None, *args, **kwargs):

        try:
            with transaction.atomic():
                password = request.data['password']
                password2 = request.data['password2']

                user = get_user_model().objects.get(pk=pk)
                
                if password != password2:
                    return Response({'detail': "Password fields didn't match."}, status=status.HTTP_400_BAD_REQUEST)
                elif len(password) < 5:
                    return Response({'detail': "Password length cannot be less than 5 characters."}, status=status.HTTP_400_BAD_REQUEST)

                UserProfile.objects.get(user=user)

                try:
                    user.set_password(password)
                    user.save()

                    update_session_auth_hash(request, user)  # Important!
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                if user.is_email_verified:
                    email_update_notifier.delay(user.id, subject='Password updated', msg="Your password was updated successfully.", origin='apps.user_profile.api.ChangePasswordViewSet', sign_off='Take care', email_to=user.email)
            
                return Response({'detail': "Your password was updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateUserEmailViewSet(APIView):
    
    permission_classes = [IsAuthenticated, IsOwnerProfileOrReadOnly]

    def patch(self, request, pk=None, *args, **kwargs):
        
        try:
            with transaction.atomic():
                email = request.data['email']

                user = get_user_model().objects.get(pk=pk)
                
                exists = get_user_model().objects.filter(email=email).exclude(id=pk, is_email_verified=False).exists()
                if exists:
                    return Response({'detail': "User with email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                
                profile = UserProfile.objects.get(user=user)
                
                if not profile.verified_email:
                    profile.verified_email = False
                    
                profile.email = email
                profile.save()

                try:
                    mail_notifier.delay(user.id, get_current_site(request).domain, origin="apps.user_profile.api.UpdateUserEmailViewSet", verification_type=2, subject='Verifying email address - Update', sign_off='Take care', email_to=email)
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                return Response({'detail': "Sending mail to your email address"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)