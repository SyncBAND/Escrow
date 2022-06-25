from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.views.generic.base import TemplateView
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from apps.user_profile.models import UserProfile
from .serializers import RegisterSerializer, UserSerializer, RegisterViewSerializer
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.utils.notifications import email_update_notifier
from apps.utils.tokens import email_verification_token

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from core.models import UserVerification

# Create your views here.


class LoginViewSet(TokenObtainPairView):
    permission_classes      = [AllowAny]


class RegisterViewSet(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LogoutViewSet(generics.GenericAPIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        logout(request)
        return Response({'detail': 'User logged out'}, status=status.HTTP_200_OK)

    def post(self, request):
        logout(request)
        return Response({'detail': 'User logged out'}, status=status.HTTP_200_OK)


class ResetPasswordViewSet(generics.GenericAPIView):

    authentication_classes = ()
    permission_classes = (AllowAny, )

    def get(self, request):
        return Response({'detail': 'Not allowed'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        
        try:
            email = request.data['email']
            user = get_user_model().objects.filter(email = email).first()

            if user:
                UserProfile.objects.filter(user = user, verified_email=True)

                subject = 'Reset your password'
                
                message = render_to_string('account_reset_email.html', {
                    'user': user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                from_email = settings.EMAIL_HOST_USER
                send_mail(
                    subject,
                    message,
                    from_email,
                    [email],
                    fail_silently = True
                )

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'If the email exists, an email was sent to reset your password'}, status=status.HTTP_200_OK)


class LogoutView(viewsets.ModelViewSet):

    model = get_user_model()
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    serializer_class = UserSerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return get_user_model().objects.filter(pk=self.kwargs['pk'])
        return None

    def post(self, request, pk=None):

        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'detail': 'User logged out'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:

            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(viewsets.ModelViewSet):
    
    model = get_user_model()
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    serializer_class = UserSerializer
    
    def get_queryset(self):
        if 'pk' in self.kwargs:
            return get_user_model().objects.filter(pk=self.kwargs['pk'])
        return None

    def post(self, request, pk=0):

        tokens = OutstandingToken.objects.filter(user_id=pk)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)
        logout(request)
        return Response({'detail': 'User logged out'}, status=status.HTTP_205_RESET_CONTENT)


''' 
Redirect from email after clicking on new email link
'''     

class VerifyEmailViewSet(TemplateView):

    template_name = "verify_email_return_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            uidb64 = kwargs['uidb64']
            token = kwargs['token']
        except Exception as e:
            context['error'] = True
            context['message'] = str(e)
            return context

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except Exception as e:
            context['error'] = True
            context['message'] = str(e)
            return context
        
        if email_verification_token.check_token(user, token):
            try:
                with transaction.atomic():
                    
                    context['message'] = 'Your email address has already been verified'
                    profile = UserProfile.objects.get(user=user)

                    verified = UserVerification.objects.filter(user=user, verified=False, expired=False, uid=uidb64, token=token)
                    
                    if verified.exists():
                        try:
                            
                            verifier = verified.first()
                            if verifier.email_address:
                                user.email = verifier.email_address
                                profile.email = verifier.email_address

                            context['message'] = 'Your email address is now verified'
                            context['error'] = False

                            #mail
                            email_update_notifier.delay(user.id, subject='Email address updated', msg="Your email was updated successfully.", origin='apps.api_auth.views.VerifyEmailViewSet', sign_off='Take care', email_to=verifier.email_address)
                    
                            profile.verified_email = True
                            profile.date_email_verified = timezone.localtime(timezone.now())
                            profile.save()

                            user.is_email_verified = True
                            user.save()

                            verified.update(verified = True, expired=True)

                        except Exception as e:
                            context['message'] = str(e)
                            context['error'] = True

            except Exception as e:
                context['message'] = str(e)
                context['error'] = True

            return context
            
        else:

            try:
                verifier = UserVerification.objects.get(user=user, verified=False, expired=False, uid=uidb64, token=token)
                verifier.expired = True
                verifier.save()
            except:
                pass

            context['error'] = True
            context['message'] = 'The url has already been used'
            return context
    

class LoginAPIViewSet(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes      = [AllowAny]

    def post(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:

            if request.user.is_superuser:
                return HttpResponseRedirect('/admin/')
            else:
                logout(request)
                return HttpResponseRedirect('http://app.metsiapp.co.za/')

        email = request.data.get('email', '')
        password = request.data.get('password', '')

        if email == '':
            return Response({'detail': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        if password == '':
            return Response({'detail': 'Password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Logged in'}, status=status.HTTP_200_OK)
            
        return Response({'detail': 'Not allowed'}, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPIViewSet(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = RegisterViewSerializer

