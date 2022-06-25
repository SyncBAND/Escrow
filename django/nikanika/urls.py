"""nikanika URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import get_version
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from apps.administrator import views as nikanika_administrator_views
from apps.api_auth import views as nikanika_api_auth_views
from apps.api_messages import views as nikanika_api_messages_views
from apps.app_payment_gateway import views as nikanika_app_payment_gateway_views
from apps.app_transactions import views as nikanika_app_transactions_views
from apps.wallet_transactions import views as nikanika_wallet_transactions_views
from apps.chat import views as nikanika_chat_views
from apps.support import views as nikanika_support_views
from apps.user_profile import views as nikanika_user_profile_views
from apps.user_profile.api import ChangePasswordViewSet, UserViewSet, UpdateUserEmailViewSet

from distutils.version import StrictVersion


api_nikanika_router = routers.DefaultRouter()

api_nikanika_router.register(r'messages', nikanika_api_messages_views.MessageViewSet, basename='nikanika-messages')
api_nikanika_router.register(r'payment-gateway', nikanika_app_payment_gateway_views.PaymentGatewayViewSet, basename='nikanika-payment-gateway')
api_nikanika_router.register(r'payment-charge-fee', nikanika_app_payment_gateway_views.PaymentChargeFeeViewSet, basename='nikanika-charge-fee')
api_nikanika_router.register(r'transactions', nikanika_app_transactions_views.TransactionViewSet, basename='nikanika-transactions')
api_nikanika_router.register(r'wallet-transactions', nikanika_wallet_transactions_views.WalletTransactionViewSet, basename='nikanika-wallet-transactions')
api_nikanika_router.register(r'withdrawal-transactions', nikanika_wallet_transactions_views.WithdrawalWalletTransactionViewSet, basename='nikanika-withdrawal-transactions')
api_nikanika_router.register(r'chat', nikanika_chat_views.ChatViewSet, basename='nikanika-chat')
api_nikanika_router.register(r'chat-list', nikanika_chat_views.ChatListViewSet, basename='nikanika-chat-list')
api_nikanika_router.register(r'support', nikanika_support_views.SupportViewSet, basename='nikanika-support')
api_nikanika_router.register(r'support-activity', nikanika_support_views.SupportActivityViewSet, basename='nikanika-support-activity')
api_nikanika_router.register(r'user-profiles', nikanika_user_profile_views.UserProfileViewSet, basename='nikanika-user-profiles')
api_nikanika_router.register(r'user-verified-profiles', nikanika_user_profile_views.UserVerifiedProfileCaseViewSet, basename='nikanika-user-verified-profile')
api_nikanika_router.register(r'user', UserViewSet, basename='nikanika-user')
api_nikanika_router.register(r'update-profile', UserViewSet, basename='nikanika-update-profile')
api_nikanika_router.register(r'logout', nikanika_api_auth_views.LogoutView, basename='nikanika-logout')
api_nikanika_router.register(r'logout-all', nikanika_api_auth_views.LogoutAllView, basename='nikanika-logout-all')


if StrictVersion(get_version()) < StrictVersion('2.0'):

    from django.conf.urls import url, include
    
    urlpatterns = [
        url(r'^admin/', admin.site.urls),

        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^api/auth/', include('apps.api_auth.urls')),
        
        url(r'^api/administrator/', include('apps.administrator.urls')),

        url(r'^api/', include(api_nikanika_router.urls)),

        url(r'^api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),

        url(r'^api/update-profile-email/(?P<pk>\d+)/$', UpdateUserEmailViewSet.as_view(), name='update_profile_email'),
        url(r'^api/update-user-password/(?P<pk>\d+)/$', ChangePasswordViewSet.as_view(), name='update_password'),
        
        url(r'^api/transactions/post/(?P<pk>\d+)/$', nikanika_app_transactions_views.PostTransactionViewSet.as_view(), name='post_transaction'),
        url(r'^api/transactions/cancel/(?P<pk>\d+)/(?P<inv>[0-9A-Z]+)/$', nikanika_app_transactions_views.CancelledTransactionViewSet.as_view(), name='cancel_transaction'),
        url(r'^api/transactions/successful/(?P<pk>\d+)/(?P<inv>[0-9A-Z]+)/$', nikanika_app_transactions_views.SuccessfulTransactionViewSet.as_view(), name='successful_transaction'),

        url(r'^$', nikanika_administrator_views.Landing.as_view(), name='landing'),
    ]

else:
    
    from django.urls import include, path

    urlpatterns = [
        path('admin/', admin.site.urls),

        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        path('api/auth/', include('apps.api_auth.urls')),
        
        path('api/administrator/', include('apps.administrator.urls')),

        path('api/', include(api_nikanika_router.urls)),

        path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

        path('api/update-profile-email/<int:pk>/', UpdateUserEmailViewSet.as_view(), name='update_profile_email'),
        path('api/update-user-password/<int:pk>/', ChangePasswordViewSet.as_view(), name='update_password'),
        
        path('api/transactions/post/<int:pk>/', nikanika_app_transactions_views.PostTransactionViewSet.as_view(), name='post_transaction'),
        path('api/transactions/cancel/<int:pk>/<str:inv>/', nikanika_app_transactions_views.CancelledTransactionViewSet.as_view(), name='cancel_transaction'),
        path('api/transactions/successful/<int:pk>/<str:inv>/', nikanika_app_transactions_views.SuccessfulTransactionViewSet.as_view(), name='successful_transaction'),

        path('', nikanika_administrator_views.Landing.as_view(), name='landing'),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
