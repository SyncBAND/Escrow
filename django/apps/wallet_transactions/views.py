from django.db import transaction
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models.functions import Concat
from django.db.models import Value
from django.utils import timezone

from rest_framework import decorators, status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.wallet_transactions.models import WalletTransaction, WithdrawalWalletTransaction
from apps.wallet_transactions.serializers import WalletTransactionSerializer, WithdrawalWalletTransactionSerializer
from apps.utils.pagination import CustomPagination
from apps.app_transactions.models import Transaction
from apps.user_profile.models import UserProfile
from apps.utils.notifications import transaction_notifier
from apps.user_profile.serializers import UserProfileSerializer


class WalletTransactionViewSet(viewsets.ModelViewSet):

    model = WalletTransaction
    serializer_class = WalletTransactionSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    search_fields = (
        'user_profile',
        'transaction',
        'wallet_reference',
        'transaction_details',
    )
    ordering_fields = (
        'id',
        'user_profile',
        'wallet_transaction',
        'created',
        'modified'
    )

    def get_queryset(self):
        
        if not self.request.user.is_authenticated:
            raise PermissionDenied()

        queryset = WalletTransaction.get_queryset(self.request.user)

        if queryset is not None:
            return queryset.order_by('-modified')

        raise PermissionDenied()

    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, ))
    def received(self, request):
        
        if request.user.is_superuser:
            queryset = WalletTransaction.objects.filter(wallet_transaction=0).order_by('-modified')
        else:
            queryset = WalletTransaction.objects.filter(wallet_transaction=0, user_profile__user=request.user).order_by('-modified')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, ))
    def withdraw(self, request):

        try:
        
            with transaction.atomic():
                transaction_reference = request.data.get('reference')
                amount = request.data.get('amount')

                withdrawal_payment = int(request.data.get('withdrawal_payment'))
                withdrawal_payment_account = int(request.data.get('withdrawal_payment_account'))
                withdrawal_account_number = request.data.get('withdrawal_account_number')
                withdrawal_cell_number = request.data.get('withdrawal_cell_number')

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


                get_transaction = Transaction.objects.get(recipient=request.user, reference=transaction_reference)

                if get_transaction.withdrawn:
                    return Response({'detail': 'Money has already been withdrawn'}, status=status.HTTP_400_BAD_REQUEST)

                if withdrawal_payment == 0:
                    if len(withdrawal_cell_number) < 10:
                        return Response({'detail': 'For E-wallet, withdrawal cell number is required'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    message = 'Withdrawal by {}.{} of R{}.\n\nPayment option: Ewallet\nCell number: {}'.format(
                        user_profile.user.id, 
                        user_profile.user.email, 
                        get_transaction.amount,
                        withdrawal_cell_number
                    )
                    
                else:
                    if len(withdrawal_account_number) < 4:
                        return Response({'detail': 'For bank payment, bank account number is required'}, status=status.HTTP_400_BAD_REQUEST)

                    message = 'Withdrawal by {}.{} of R{}.\n\nBank name:{}\nBank account type: {}\nBank account number: {}\nReference: {}'.format(
                        user_profile.user.id, 
                        user_profile.user.email, 
                        get_transaction.amount,
                        WithdrawalWalletTransaction._withdrawal_payment_choices[withdrawal_payment],
                        WithdrawalWalletTransaction._withdrawal_payment_account_type_choices[withdrawal_payment_account],
                        withdrawal_account_number,
                        transaction_reference
                    )

                if get_transaction.goods_delivered:

                    try:
                        wallet_transaction = WalletTransaction.objects.get(
                            user_profile=user_profile, 
                            transaction=get_transaction, 
                            transaction_amount=amount, 
                            wallet_transaction=1
                        )
                    except:
                        WalletTransaction.objects.filter(
                            user_profile=user_profile, 
                            transaction=get_transaction, 
                            wallet_transaction=1
                        ).update(wallet_transaction=3, transaction_details=Concat('transaction_details', Value('\n\n{} - Cancelled: change of withdrawal details'.format( timezone.localtime(timezone.now()) ))))

                        wallet_transaction = WalletTransaction.objects.create(
                            user_profile=user_profile, 
                            transaction=get_transaction, 
                            previous_wallet_amount=user_profile.wallet, 
                            transaction_amount=amount, 
                            transaction_details="Withdrawal",
                            wallet_transaction=1
                        )
                        
                    try:
                        WithdrawalWalletTransaction.objects.get(
                            wallet_transaction=wallet_transaction,
                            amount=amount,
                            withdrawal_payment=withdrawal_payment,
                            withdrawal_payment_account=withdrawal_payment_account,
                            withdrawal_account_number=withdrawal_account_number,
                            withdrawal_cell_number=withdrawal_cell_number,
                            withdrawal_reference=transaction_reference,
                            status=0
                        )
                        get_transaction.withdrawal_status = 0
                        get_transaction.save()
                    except:
                        WithdrawalWalletTransaction.objects.filter(
                            wallet_transaction=wallet_transaction,
                            status=0
                        ).update(status=2, status_details=Concat('status_details', Value('\n\n{} - Cancelled: change of withdrawal details'.format( timezone.localtime(timezone.now()) ))))

                        WithdrawalWalletTransaction.objects.create(
                            wallet_transaction=wallet_transaction,
                            amount=amount,
                            withdrawal_payment=withdrawal_payment,
                            withdrawal_payment_account=withdrawal_payment_account,
                            withdrawal_account_number=withdrawal_account_number,
                            withdrawal_cell_number=withdrawal_cell_number,
                            withdrawal_reference=transaction_reference,
                        )
                        get_transaction.withdrawal_status = 0
                        get_transaction.save()

                        user_profile.withdrawal_payment=withdrawal_payment
                        user_profile.withdrawal_payment_account=withdrawal_payment_account
                        user_profile.withdrawal_account_number=withdrawal_account_number
                        user_profile.withdrawal_cell_number=withdrawal_cell_number
                        user_profile.withdrawal_reference=transaction_reference
                        user_profile.save()

                        transaction_notifier.delay(
                            user_profile.user.id,
                            origin='WalletTransactionViewset.withdrawal', 
                            subject='#Urgent - User withdrawal: {}'.format(transaction_reference), 
                            message=message,
                            email_to=[settings.EMAIL_HOST_USER],
                            user_receiving_mail=1
                        )
                    
                else:
                    return Response({'detail': 'Goods/Services are not delivered as yet'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = UserProfileSerializer(user_profile, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, ))
    def withdrawal_money_sent(self, request):
        
        try:
            id = request.data.get('id')
            details = request.data.get('details', 'Sent')

            if request.user.is_superuser or request.user.is_staff:
                withdrawal = WithdrawalWalletTransaction.objects.get(id=id, status=0)
                withdrawal.approved_by = request.user
                withdrawal.status = 1
                withdrawal.status_details = '{}\n\n{} - Completed: {}'.format(withdrawal.status_details, timezone.localtime(timezone.now()), details)
                withdrawal.save()

                withdrawal.wallet_transaction.transaction.withdrawn = True
                withdrawal.wallet_transaction.transaction.withdrawal_status = 1
                withdrawal.wallet_transaction.transaction.logs = '{}\n\n{} - Completed: {}'.format(withdrawal.wallet_transaction.transaction.logs, timezone.localtime(timezone.now()), details)
                withdrawal.wallet_transaction.transaction.save()

                transaction_notifier.delay(
                    withdrawal.wallet_transaction.user_profile.user.id,
                    origin='WalletTransactionViewset.withdrawal_money_sent', 
                    subject='Withdrawal: {}'.format(withdrawal.wallet_transaction.transaction.reference),
                    message="Withdrawal is completed",
                    email_to=[withdrawal.wallet_transaction.user_profile.user.email]
                )
                transaction_notifier.delay(
                    request.user.id,
                    origin='WalletTransactionViewset.withdrawal_money_sent', 
                    subject='#Urgent - User withdrawal: {}'.format(withdrawal.wallet_transaction.transaction.reference), 
                    message="Withdrawal was completed by {}.{}".format(request.user.id, request.user.email),
                    email_to=[settings.EMAIL_HOST_USER],
                    user_receiving_mail=1
                )
                
            else:
                return Response({'detail': "Not permitted"}, status=status.HTTP_401_UNAUTHORIZED)
        
            return Response({'detail': 'Done'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, ))
    def withdrawal_money_reversal(self, request):
        
        try:
            id = request.data.get('id')
            details = request.data.get('details', 'Reversed')

            if request.user.is_superuser or request.user.is_staff:
                withdrawal = WithdrawalWalletTransaction.objects.get(id=id, status=0)
                withdrawal.reversed_by = request.user
                withdrawal.status = 3
                withdrawal.status_details = '{}\n\n{} - Reversed: {}'.format(withdrawal.status_details, timezone.localtime(timezone.now()), details)
                withdrawal.save()

                withdrawal.wallet_transaction.transaction.withdrawn = False
                withdrawal.wallet_transaction.transaction.withdrawal_status = 3
                withdrawal.wallet_transaction.transaction.logs = '{}\n\n{} - Reversed: {}'.format(withdrawal.wallet_transaction.transaction.logs, timezone.localtime(timezone.now()), details)
                withdrawal.wallet_transaction.transaction.save()

                WalletTransaction.objects.create(
                    user_profile=withdrawal.wallet_transaction.user_profile, 
                    transaction=withdrawal.wallet_transaction.transaction, 
                    previous_wallet_amount=withdrawal.wallet_transaction.user_profile.wallet, 
                    transaction_amount=withdrawal.amount, 
                    transaction_details=details,
                    wallet_transaction=3
                )
                transaction_notifier.delay(
                    request.user.id,
                    origin='WalletTransactionViewset.withdrawal_money_reversal', 
                    subject='#Urgent - User withdrawal: {}'.format(withdrawal.wallet_transaction.transaction.reference), 
                    message="Withdrawal was reversed by {}.{} - Details: {}".format(request.user.id, request.user.email, details),
                    email_to=[settings.EMAIL_HOST_USER],
                    user_receiving_mail=1
                )

            else:
                return Response({'detail': "Not permitted"}, status=status.HTTP_401_UNAUTHORIZED)
        
            return Response({'detail': 'Done'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WithdrawalWalletTransactionViewSet(viewsets.ModelViewSet):

    model = WithdrawalWalletTransaction
    serializer_class = WithdrawalWalletTransactionSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    search_fields = (
        'status_details',
        'withdrawal_account_number',
        'withdrawal_cell_number',
        'withdrawal_reference',
    )
    ordering_fields = (
        'id',
        'withdrawal_payment',
        'created',
        'modified'
    )

    def list(self, request):

        if request.user.is_superuser:
            queryset = WithdrawalWalletTransaction.objects.all()
        else:
            queryset = WithdrawalWalletTransaction.objects.filter(wallet_transaction__user_profile__user=request.user)
    
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, ))
    def details(self, request):
        
        try:
            transaction_id = request.GET.get('transaction_id')
            
            if request.user.is_superuser:
                queryset = WithdrawalWalletTransaction.objects.filter(wallet_transaction__transaction=transaction_id)
            else:
                queryset = WithdrawalWalletTransaction.objects.filter(wallet_transaction__transaction=transaction_id, wallet_transaction__user_profile__user=request.user)
        
            page = self.paginate_queryset(queryset.order_by('-modified'))
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)