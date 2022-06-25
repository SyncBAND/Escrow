from django.db.models import Q, Value
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models.functions import Concat
from django.utils import timezone
from django.db import transaction
from django.views.generic.base import TemplateView

from rest_framework import viewsets, pagination, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Transaction
from .serializers import TransactionSerializer
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.user_profile.models import UserProfile, UserRatings, UserRatingsHistory
from apps.app_payment_gateway.models import PaymentGateway
from apps.utils.views import pfValidSignature, validIP
from apps.wallet_transactions.models import WalletTransaction
from apps.utils.notifications import transaction_notifier

from decimal import Decimal


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
 

class TransactionViewSet(viewsets.ModelViewSet):

    model = Transaction
    serializer_class = TransactionSerializer
    pagination_class = Pagination

    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    
    # def get_object(self):
    
    #     try:
    #         user = self.request.user
    #         if user.is_superuser or user.is_staff:
    #             return UserProfile.objects.get(user_id=self.kwargs.get("pk"))

    #         if int(user.id) == int(self.kwargs.get("pk")):
    #             return UserProfile.objects.get(user_id=self.kwargs.get("pk"))
            
    #         return super().get_object()
    #     except:
    #         return super().get_object()

    def list(self, request):

        if request.user.is_superuser:
            queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(Q(payer=request.user) | Q(recipient=request.user))
    
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, ))
    def recieved(self, request):

        try:
            pk = int(request.GET.get('pk'))

            if request.user.is_superuser:
                pass
            else:
                if request.user.id != pk:
                    return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)

            queryset = Transaction.objects.filter(recipient_id=pk).order_by('-modified')
                    
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, ))
    def paid(self, request):

        try:
            pk = int(request.GET.get('pk'))
            
            if request.user.is_superuser:
                pass
            else:
                if request.user.id != pk:
                    return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)

            queryset = Transaction.objects.filter(payer_id=pk).order_by('-modified')
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def initiated(self, request):
        
        if request.user.is_superuser:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Initiated).order_by('-modified')
        else:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Initiated).filter(Q(payer=request.user) | Q(recipient=request.user)).order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def pending(self, request):
        
        if request.user.is_superuser:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Pending).order_by('-modified')
        else:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Pending).filter(Q(payer=request.user) | Q(recipient=request.user)).order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def complete(self, request):

        if request.user.is_superuser:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Complete).order_by('-modified')
        else:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Complete).filter(Q(payer=request.user) | Q(recipient=request.user)).order_by('-modified')
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def cancelled(self, request):

        if request.user.is_superuser:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Cancelled).order_by('-modified')
        else:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Cancelled).filter(Q(payer=request.user) | Q(recipient=request.user)).order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def refund(self, request):

        if request.user.is_superuser:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Refund).order_by('-modified')
        else:
            queryset = Transaction.objects.filter(status=Transaction.STATUS_TYPE.Refund).filter(Q(payer=request.user) | Q(recipient=request.user)).order_by('-modified')
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, ))
    def initiate(self, request):

        try:
            with transaction.atomic():
                
                password = request.data.get('password')
                user = authenticate(request, email=request.user.email, password=password)

                if user is None:
                    return Response({'detail': 'Password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
                
                user_profile = UserProfile.objects.get(user=user)

                if not user.is_email_verified:
                    return Response({'detail': 'Please verify your email address'}, status=status.HTTP_400_BAD_REQUEST)

                elif not user_profile.verified_details:
                    if user_profile.verified_details_status == 0:
                        return Response({'detail': 'Please verify your details'}, status=status.HTTP_400_BAD_REQUEST)
                    elif user_profile.verified_details_status == 1:
                        return Response({'detail': 'Your documents are still being processed.'}, status=status.HTTP_400_BAD_REQUEST)

                request.data.pop('password', None)

                share_code = request.data.get('share_code')
                details = request.data.get('details')
                amount = request.data.get('amount')
                original_amount = request.data.get('original_amount')
                calculated_charge = request.data.get('calculated_charge')
                percentage_charge = request.data.get('percentage_charge')
                flat_fee = request.data.get('flat_fee')
                gateway = request.data.get('payment_gateway')

                payment_gateway = PaymentGateway.objects.get(id=gateway)

                if payment_gateway.is_wallet:
                    if user_profile.wallet < Decimal(amount):
                        return Response({'detail': 'Insufficient funds in wallet'}, status=status.HTTP_400_BAD_REQUEST)

                recipient = UserProfile.objects.get(share_code=share_code)

                payer = request.user

                if Decimal(amount) <= 100.00:
                    return Response({'detail': 'Amount has to more than R100'}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    tr = Transaction.objects.get(payer=payer, recipient=recipient.user, payment_gateway=payment_gateway, amount=amount, original_amount=original_amount, calculated_charge=calculated_charge, percentage_charge=percentage_charge, flat_fee=flat_fee, status=0)
                    tr.share_code=share_code
                    tr.payload_request=request.data
                    tr.details=details
                    tr.notify_url = 'http://c168-196-11-159-242.ngrok.io/api/transactions/payment_result/'
                    # tr.notify_url=request.build_absolute_uri("/api/transactions/payment_result/")
                    tr.return_url=request.build_absolute_uri( "/api/transactions/successful/{}/{}/".format(tr.id, tr.reference) )
                    tr.cancel_url=request.build_absolute_uri( "/api/transactions/cancel/{}/{}/".format(tr.id, tr.reference) )
                    tr.save()

                except Exception as e:
                    Transaction.objects.filter(payer=payer, recipient=recipient.user, amount=amount, original_amount=original_amount, calculated_charge=calculated_charge, percentage_charge=percentage_charge, flat_fee=flat_fee, payment_gateway=payment_gateway, status=0).update(status=3, details=Concat('details', Value('\n\n{} - Cancel - {}'.format( timezone.localtime(timezone.now()), str(e) ))))
                    
                    tr = Transaction.objects.create(
                        payer=payer, 
                        recipient=recipient.user, 
                        share_code=share_code,
                        details=details, 
                        payment_gateway=payment_gateway,
                        amount=amount,
                        original_amount=original_amount,
                        calculated_charge=calculated_charge, 
                        percentage_charge=percentage_charge, 
                        logs='{} - {}: Initated'.format( timezone.localtime(timezone.now()), payment_gateway.name), 
                        flat_fee=flat_fee, 
                        notify_url = 'http://c168-196-11-159-242.ngrok.io/api/transactions/payment_result/',
                        payload_request=request.data
                    )
                    # notify_url=request.build_absolute_uri("/api/transactions/payment_result/"),
                    # notify_url = 'http://c168-196-11-159-242.ngrok.io/api/transactions/payment_result/',
                    tr.return_url=request.build_absolute_uri( "/api/transactions/successful/{}/{}/".format(tr.id, tr.reference) )
                    tr.cancel_url=request.build_absolute_uri( "/api/transactions/cancel/{}/{}/".format(tr.id, tr.reference) )
                    tr.save()


                if payment_gateway.is_wallet: 
                    tr.payload_response = request.data
                    tr.status = 2
                    tr.logs = "{}\n\n{} - Wallet payment: COMPLETE".format( tr.logs, timezone.localtime(timezone.now()) )
                    tr.save()

                    WalletTransaction.objects.create(user_profile=recipient, transaction=tr, previous_wallet_amount=recipient.wallet, transaction_amount=tr.original_amount, transaction_details="Recieved from {}".format(user_profile.user.email))
                    
                    WalletTransaction.objects.create(user_profile=user_profile, transaction=tr, previous_wallet_amount=user_profile.wallet, transaction_amount=tr.original_amount, transaction_details="Payment made to {}".format(recipient.user.email), wallet_transaction=2)

                    transaction_notifier.delay(
                        tr.payer.id,
                        origin='TransactionViewset.payment_result', 
                        subject='Wallet payment made: {}'.format(tr.reference), 
                        message='Payment was made from {}.{} to {}.{} ({}) of R{} - Details: {}. Reference: {}.'.format(tr.payer.id, tr.payer.email, tr.recipient.id, tr.recipient.email, tr.share_code, tr.amount, tr.details, tr.reference), 
                        email_to=[settings.EMAIL_HOST_USER],
                        user_receiving_mail=1
                    )

            if payment_gateway.request_redirect_url:
                response = payment_gateway.make_payment(transaction=tr, return_url=request.build_absolute_uri("/api/transactions/payment_result/"))
            else:
                response = {
                    'url': request.build_absolute_uri("/api/transactions/post/{}/".format(tr.id)),
                    'redirect': payment_gateway.redirect
                }
            
            return Response({'transaction_id': tr.id, 'response': response}, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=['post'], permission_classes = (AllowAny, ))
    def payment_result(self, request):
        
        try:

            with transaction.atomic():

                if 'payment_status' in request.data:

                    amount = request.data.get('amount_gross', None)
                    signature = request.data.get('signature', None)
                    reference = request.data.get('m_payment_id', None)

                    if not signature:
                        try:
                            signature = request.POST.get('signature')
                        except Exception as e:
                            return Response({'detail': 'Not permitted'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    tr = Transaction.objects.get(amount=amount, reference=reference, status=0)

                    tr.payload_response = request.data

                    pf = pfValidSignature(request.data, signature)
                    ip = validIP(request.headers)

                    if pf and ip:
                        '''
                        most likely Payfast response
                        '''
                        
                        if request.data['payment_status'] == 'COMPLETE':

                            tr.status = 2
                            tr.logs = "{}\n\n{} - Payfast: COMPLETE".format(tr.logs, timezone.localtime(timezone.now()))

                            tr.pf_m_payment_id = reference
                            tr.pf_pf_payment_id = request.data.get('pf_payment_id', None)
                            tr.pf_payment_status = request.data.get('payment_status', None)
                            tr.pf_item_name = request.data.get('item_name', None)
                            tr.pf_item_description = request.data.get('item_description', None)
                            tr.pf_amount_gross = request.data.get('amount_gross', None)
                            tr.pf_amount_fee = request.data.get('amount_fee', None)
                            tr.pf_amount_net = request.data.get('amount_net', None)

                            user_profile = UserProfile.objects.get(user=tr.recipient)
                            
                            WalletTransaction.objects.create(user_profile=user_profile, transaction=tr, previous_wallet_amount=user_profile.wallet, transaction_amount=tr.original_amount, transaction_details="Recieved from {}".format(tr.payer.email))

                            transaction_notifier.delay(
                                tr.payer.id,
                                origin='TransactionViewset.payment_result', 
                                subject='Payfast payment made: {}'.format(reference), 
                                message='You have made payment to {} ({}) of R{} - Details: {}. Reference: {}.\n\nOnce the goods or services have been delivered to you, the money will be released to the recipient.'.format(tr.recipient.email, tr.share_code, tr.amount, tr.details, tr.reference), 
                                email_to=[tr.payer.email]
                            )

                            transaction_notifier.delay(
                                tr.payer.id,
                                origin='TransactionViewset.payment_result', 
                                subject='Payfast payment made: {}'.format(reference), 
                                message='Payment was made from {}.{} to {}.{} ({}) of R{} - Details: {}. Reference: {}.'.format(tr.payer.id, tr.payer.email, tr.recipient.id, tr.recipient.email, tr.share_code, tr.amount, tr.details, tr.reference), 
                                email_to=[settings.EMAIL_HOST_USER],
                                user_receiving_mail=1
                            )

                        else:
                            tr.status = 3
                            tr.cancellation_reason = "Payfast: Transaction cancelled"
                            tr.logs = "{}\n\n{} - Payfast: CANCELLED".format(tr.logs, timezone.localtime(timezone.now()))
                    
                    elif not ip:
                        return Response({'detail': 'IP is not valid'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        return Response({'detail': 'Signature verification is not invalid'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    tr.save()

                elif 'success' in request.data:
                    '''
                    possibly Airbuy
                    '''

                    reference = request.data['id']
                    tr = Transaction.objects.get(reference=reference, status=0)

                    tr.payload_response = request.data
                    
                    message = ''
                    if 'message' in request.data:
                        message = request.data['message']
                    
                    success = request.data.get('success')
                    
                    if success == 'True':
                        tr.status = 2
                        tr.logs = "{}\n\n{} - Airbuy: COMPLETE - {}".format( tr.logs, timezone.localtime(timezone.now()), message )

                        user_profile = UserProfile.objects.get(user=tr.recipient)
                        WalletTransaction.objects.create(user_profile=user_profile, transaction=tr, previous_wallet_amount=user_profile.wallet, transaction_amount=tr.original_amount, transaction_details="Recieved from {}".format(tr.payer.email))
                        
                        transaction_notifier.delay(
                            tr.payer.id, 
                            origin='TransactionViewset.payment_result', 
                            subject='Airbuy payment made: {}'.format(reference), 
                            message='You have made payment to {} ({}) of R{} - Details: {}. Reference: {}.\n\nOnce the goods or services have been delivered to you, the money will be released to the recipient.'.format(tr.recipient.email, tr.share_code, tr.amount, tr.details, reference), 
                            email_to=[tr.payer.email]
                        )

                        transaction_notifier.delay(
                            tr.payer.id, 
                            origin='TransactionViewset.payment_result', 
                            subject='Airbuy payment made: {}'.format(reference), 
                            message='Payment was made from {}.{} to {}.{} ({}) of R{} - Details: {}. Reference: {}.'.format(tr.payer.id, tr.payer.email, tr.recipient.id, tr.recipient.email, tr.share_code, tr.amount, tr.details, reference), 
                            email_to=[settings.EMAIL_HOST_USER],
                            user_receiving_mail=1
                        )

                    else:
                        tr.status = 3
                        tr.cancellation_reason = "Airbuy: Transaction cancelled"
                        tr.logs = "{}\n\n{} - Airbuy: CANCELLED - {}".format( tr.logs, timezone.localtime(timezone.now()), message  )
                        
                    tr.save()

                elif 'wallet_payment' in request.data:
                    '''
                    possibly Wallet
                    '''

                    reference = request.data['reference']
                    tr = Transaction.objects.get(reference=reference, status=0)

                    if request.user.is_authenticated:
                        
                        profile = UserProfile.objects.get(user=request.user)

                        if profile.wallet >= tr.amount:

                            tr.payload_response = request.data
                            tr.status = 2
                            tr.logs = "{}\n\n{} - Wallet payment: COMPLETE - {}".format( tr.logs, timezone.localtime(timezone.now()), message )
                            tr.save()

                            user_profile = UserProfile.objects.get(user=tr.recipient)
                            WalletTransaction.objects.create(user_profile=user_profile, transaction=tr, previous_wallet_amount=user_profile.wallet, transaction_amount=tr.original_amount, transaction_details="Recieved from {}".format(tr.payer.email))
                            
                            WalletTransaction.objects.create(user_profile=profile, transaction=tr, previous_wallet_amount=profile.wallet, transaction_amount=tr.original_amount, transaction_details="Payment made to {}".format(tr.recipient.email), wallet_transaction=2)

                            transaction_notifier.delay(
                                tr.payer.id,
                                origin='TransactionViewset.payment_result', 
                                subject='Wallet payment made: {}'.format(reference), 
                                message='Payment was made from {}.{} to {}.{} ({}) of R{} - Details: {}. Reference: {}.'.format(tr.payer.id, tr.payer.email, tr.recipient.id, tr.recipient.email, tr.share_code, tr.amount, tr.details, tr.reference), 
                                email_to=[settings.EMAIL_HOST_USER],
                                user_receiving_mail=1
                            )

                        else:
                            tr.status = 3
                            tr.cancellation_reason = "Wallet: Insufficient funds"
                            tr.logs = "{}\n\n{} - Wallet: Insufficient funds".format( tr.logs, timezone.localtime(timezone.now()) )
                            tr.save()
                            return Response({'detail': 'Insufficient funds in wallet'}, status=status.HTTP_400_BAD_REQUEST)
                            
                    else:

                        return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)

                return Response({'detail': 'Successful'}, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  

    @decorators.action(detail=False, methods=['patch'], permission_classes = (IsAuthenticated, ))
    def delivered(self, request):
        
        try:

            with transaction.atomic():

                id = request.data.get('id', None)
                reference = request.data.get('reference', None)
                details = request.data.get('details', None)

                if request.user.is_superuser or request.user.is_staff:
                    tr = Transaction.objects.get(id=id, reference=reference, status=2)
                    rating = None
                else:
                    tr = Transaction.objects.get(id=id, reference=reference, status=2, payer=request.user)
                    rating = int(request.data.get('rating', None))

                    if rating is None or rating == 0:
                        return Response({'detail': 'Rating was not given'}, status=status.HTTP_400_BAD_REQUEST)
                
                # rating
                if request.user == tr.payer:

                    # payer
                    user_profile_making_rating = UserProfile.objects.get(user=tr.payer) 
                    # recipient
                    user_profile_being_rated = UserProfile.objects.get(user=tr.recipient) 

                    try:
                        
                        user_ratings = UserRatings.objects.get(user_profile_making_rating=user_profile_making_rating, user_profile_being_rated=user_profile_being_rated, transaction_id=tr.id)
                        
                        UserRatingsHistory.objects.create(user_ratings=user_ratings, previous_rating=user_ratings.rating, previous_review=user_ratings.review)
                        
                        # if editting, minus previous rating and add new one
                        # user_profile_being_rated rating FROM user_profile_making_rating
                        user_profile_being_rated.total_sum_of_ratings_from_users = user_profile_being_rated.total_sum_of_ratings_from_users - user_ratings.rating + rating
                        user_profile_being_rated.save()

                        # user_profile_making_rating rating an user_profile_being_rated
                        user_profile_making_rating.total_sum_of_ratings_for_users = user_profile_making_rating.total_sum_of_ratings_for_users - user_profile_being_rated.rating + rating
                        user_profile_making_rating.save()

                        user_ratings.review = details
                        user_ratings.rating = rating
                        user_ratings.editted = True
                        user_ratings.save()

                    except:
                        
                        UserRatings.objects.create(user_profile_making_rating=user_profile_making_rating, user_profile_being_rated=user_profile_being_rated, review=details, rating=rating, transaction_id=tr.id)
                        
                        # to get rating percentage = (user_profile_being_rated.total_sum_of_ratings_from_users/5)/user_profile_being_rated.total_number_of_ratings_from_users
                        user_profile_being_rated.total_sum_of_ratings_from_users = user_profile_being_rated.total_sum_of_ratings_from_users + rating
                        user_profile_being_rated.total_number_of_ratings_from_users = user_profile_being_rated.total_number_of_ratings_from_users + 1
                        user_profile_being_rated.save()
                    
                        # user_profile_making_rating rating an user_profile_being_rated
                        user_profile_making_rating.total_sum_of_ratings_for_users = user_profile_making_rating.total_sum_of_ratings_for_users + rating
                        user_profile_making_rating.total_number_of_ratings_for_users = user_profile_making_rating.total_number_of_ratings_for_users + 1
                        user_profile_making_rating.save()
                    
                tr.goods_delivered = True
                tr.goods_delivered_details = details
                tr.rating = rating
                tr.logs = "{}\n\n{} - Delivered: Successful. made by - {}".format( tr.logs, timezone.localtime(timezone.now()), request.user.id )
                tr.save()

                serializer = self.get_serializer(tr, context={'request': request})
        
                return Response(serializer.data, status=status.HTTP_200_OK)
                
        except Exception as e:
            print(e)
            Transaction.objects.filter(reference=reference).update(logs=Concat('logs', Value('\n\n{} - Delivered Error: {} - {}'.format( timezone.localtime(timezone.now()), str(e), str(request.data) ))))
                    
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostTransactionViewSet(TemplateView):
    ''' 
    Post transaction
    '''   

    template_name = "post.html"
    
    def dispatch(self, request, *args, **kwargs):
        
        kwargs['exists'] = False
        
        if 'pk' in kwargs:
            try:
                tr = Transaction.objects.get(id=int(kwargs['pk']))

                if request.user == tr.payer:
                    
                    kwargs['data'] = {
                        'merchant_id': tr.payment_gateway.api,
                        'merchant_key': tr.payment_gateway.merchant_key,
                        'item_name': tr.details,
                        'm_payment_id': tr.reference,
                        'amount': tr.amount,
                        'email_address': tr.payer.email,
                        'signature': tr.signature,
                        'notify_url': request.build_absolute_uri("/api/transactions/payment_result/"),
                        'return_url': request.build_absolute_uri("/api/transactions/return/{}/".format(tr.id)),
                        'cancel_url': request.build_absolute_uri("/api/transactions/cancel/{}/".format(tr.id)),
                    }

                    kwargs['exists'] = True
                    kwargs['redirect'] = tr.payment_gateway.redirect_url

            except:
                pass

        return super().dispatch(request, *args, **kwargs)


class CancelledTransactionViewSet(TemplateView):
    ''' 
    Cancelled transaction
    '''   

    template_name = "cancel.html"
    
    def dispatch(self, request, *args, **kwargs):
        
        kwargs['exists'] = False
        if 'pk' in kwargs and 'inv' in kwargs:
            try:
                tr = Transaction.objects.get(id=int(kwargs['pk']), reference=kwargs['inv'])
                tr.cancellation_reason = "Payfast response: Transaction cancelled"
                tr.logs = "{}\n\n{} - Payfast response: Cancelled".format(tr.logs, timezone.localtime(timezone.now()) )
                tr.status = 3
                tr.save()
                kwargs['exists'] = True
            except:
                pass

        return super().dispatch(request, *args, **kwargs)


class SuccessfulTransactionViewSet(TemplateView):
    ''' 
    Successful transaction
    '''   

    template_name = "return.html"
    
    def dispatch(self, request, *args, **kwargs):
        
        kwargs['exists'] = False
        if 'pk' in kwargs and 'inv' in kwargs:
            try:
                tr = Transaction.objects.get(id=int(kwargs['pk']), reference=kwargs['inv'])
                tr.logs = "{}\n\n{} - Payfast response: Returned".format(tr.logs, timezone.localtime(timezone.now()) )
                tr.save()
                kwargs['exists'] = True
            except:
                pass

        return super().dispatch(request, *args, **kwargs)