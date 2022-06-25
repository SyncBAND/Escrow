from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth import logout

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.app_transactions.models import Transaction
from apps.user_profile.models import UserProfile, UserVerifiedProfileCase
from apps.support.models import Support
from apps.wallet_transactions.models import WithdrawalWalletTransaction


''' 
Redirect from email after clicking on new email link
'''     

class Landing(TemplateView):

    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:

            if request.user.is_superuser:
                return HttpResponseRedirect('/api/administrator/')
            else:
                #return HttpResponseRedirect('http://localhost:8100')
                return HttpResponseRedirect('http://nikaapp.metsiapp.co.za')
            
        return super(Landing, self).dispatch(request, *args, **kwargs)


''' 
Redirect from email after clicking on new email link
'''     

class AdminViewSet(TemplateView):

    template_name = "admin.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:

            if not request.user.is_superuser: 
                logout(request)
                #return HttpResponseRedirect('http://localhost:8100')
                return HttpResponseRedirect('https://nikaapp.metsiapp.co.za/')
        else:
            #return HttpResponseRedirect('http://localhost:8100')
            return HttpResponseRedirect('https://nikaapp.metsiapp.co.za/')
            
        return super(AdminViewSet, self).dispatch(request, *args, **kwargs)
    

class AdminDashboardViewSet(generics.GenericAPIView):

    permission_classes = (IsAuthenticated, )
    
    def get(self, request):

        if request.user.is_superuser or request.user.is_staff:

            user_profiles = UserProfile.objects.count()
            process_profiles = UserProfile.objects.filter(verified_details_status=UserProfile.VERIFIED_DETAILS_TYPE.Processing).count()
            transactions = Transaction.objects.count()
            support = Support.objects.filter(status=Support.STATUS_TYPE.Processing).count()
            process_withdrawals = WithdrawalWalletTransaction.objects.filter(status=WithdrawalWalletTransaction.STATUS_TYPE.Processing).count()

            context = {
                'user_profiles': user_profiles,
                'process_profiles': process_profiles,
                'transactions': transactions,
                'support': support,
                'process_withdrawals': process_withdrawals,
            }
            return Response(context)
        
        else:
            return Response(context, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        return
        