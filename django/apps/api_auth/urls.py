"""login_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from rest_framework_simplejwt import views as jwt_views

from apps.api_auth import views as api_auth_views

urlpatterns = [
    url(r'^login/$', api_auth_views.LoginViewSet.as_view(), name='api_auth_login'),
    url(r'^login-view/$', api_auth_views.LoginAPIViewSet.as_view(), name='api_auth_login_view'),
    url(r'^logout/$', api_auth_views.LogoutViewSet.as_view(), name='api_auth_logout'),

    url(r'^login/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    
    url(r'^register-user/$', api_auth_views.RegisterViewSet.as_view(), name='api_auth_register_user'),
    url(r'^register-view/$', api_auth_views.RegisterAPIViewSet.as_view(), name='api_auth_register_view_user'),
    url(r'^reset-password/$', api_auth_views.ResetPasswordViewSet.as_view(), name='api_auth_reset_pass'),

    url(r'^verify-email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        api_auth_views.VerifyEmailViewSet.as_view(), name='api_auth_verify_email'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
        
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
]