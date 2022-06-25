from django.db import models, transaction as db_transaction
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.utils.models import CreatedModifiedMixin, PermissionsMixin
from apps.utils.views import get_field_choices, random_generator
from apps.app_transactions.models import Transaction
from apps.user_profile.models import UserProfile
from apps.utils.notifications import transaction_notifier

from collections import namedtuple


class WalletTransaction(CreatedModifiedMixin, PermissionsMixin):
    
    user_profile = models.ForeignKey(UserProfile, blank=False, null=False, on_delete=models.CASCADE)
    
    transaction = models.ForeignKey(Transaction, null=True, blank=True, on_delete=models.SET_NULL)

    wallet_reference = models.CharField(max_length=255, null=True, blank=True)

    previous_wallet_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    transaction_amount = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
  
    transaction_choices = (
        'Received',
        'Withdrawal',
        'Paid',
        'Refund',
    )
    TRANSACTION_TYPE = namedtuple('TRANSACTION_TYPE', transaction_choices)(*range(0, len(transaction_choices)))
    wallet_transaction = models.PositiveIntegerField(default=0, choices=get_field_choices(TRANSACTION_TYPE))
    transaction_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}. {} - {}".format(self.id, self.wallet_reference, self.transaction.reference)

    def save(self, *args, **kwargs):

        with db_transaction.atomic():
            if not self.wallet_reference:
                while True:
                    wallet_reference = random_generator(length=9, letters=True, digits=True, punctuation=False)
                    if not type(self).objects.filter(wallet_reference=wallet_reference).exists():
                        break
                self.wallet_reference = wallet_reference
                
            super(WalletTransaction, self).save(*args, **kwargs)

            if self.wallet_transaction == 0:
                #  received income
                self.user_profile.wallet = float(self.user_profile.wallet) + float(self.transaction_amount)
                subject = 'Received payment: {}'.format(self.transaction.reference)
                message = 'You have received payment from {} of R{} - Details: {}. Reference: {}.\n\nOnce the goods or services have been delivered you should be able to withdraw your money.\n\nCurrent wallet balance: R{}'.format(self.transaction.payer.email, self.transaction_amount, self.transaction.details, self.transaction.reference, self.user_profile.wallet)

            elif self.wallet_transaction == 1:
                # withdrawal
                if float(self.user_profile.wallet) < float(self.transaction_amount):
                    raise ValidationError('Amount ({}) exceeds wallet balance ({})'.format(self.transaction_amount, self.user_profile.wallet))
                self.user_profile.wallet = float(self.user_profile.wallet) - float(self.transaction_amount)
                subject = 'Withdrawal: {}'.format(self.transaction.reference)
                message = 'You have withdrawn R{} from your wallet. Reference: {}. The transaction is currently been processed. \n\nCurrent wallet balance: R{}'.format(self.transaction_amount, self.transaction.reference, self.user_profile.wallet)
                
            elif self.wallet_transaction == 2:
                # paid
                if float(self.user_profile.wallet) < float(self.transaction_amount):
                    raise ValidationError('Amount ({}) exceeds wallet balance ({})'.format(self.transaction_amount, self.user_profile.wallet))
                self.user_profile.wallet = float(self.user_profile.wallet) - float(self.transaction_amount)
                subject = 'Payment made: {}'.format(self.transaction.reference)
                message = 'You have made payment to {} of R{} - Details: {}. Reference: {}.\n\nCurrent wallet balance: R{}'.format(self.transaction.recipient.email, self.transaction_amount, self.transaction.details, self.transaction.reference, self.user_profile.wallet)

            else:
                # refund
                self.user_profile.wallet = float(self.user_profile.wallet) + float(self.transaction_amount)
                subject = 'Refund: {}'.format(self.wallet_transaction)
                message = 'You have received a refund of R{} - Details: {}. Reference: {}.\n\nCurrent wallet balance: R{}'.format(self.transaction_amount, self.transaction_details, self.wallet_transaction, self.user_profile.wallet)

            transaction_notifier.delay(
                self.user_profile.user.id, origin='WalletTransaction.save', subject=subject, message=message, email_to=[self.user_profile.user.email]
            )

            self.user_profile.save()

    
    @classmethod
    def get_queryset(cls, user):

        if not user.is_authenticated:
            return WalletTransaction.objects.none()

        if user.is_superuser or user.is_staff:
            return WalletTransaction.objects.all()

        return WalletTransaction.objects.filter(user_profile__user=user)


class WithdrawalWalletTransaction(CreatedModifiedMixin, PermissionsMixin):

    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,on_delete=models.SET_NULL, related_name='withdrawal_approved_by')
    reversed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,on_delete=models.SET_NULL, related_name='withdrawal_reversed_by')
    
    wallet_transaction = models.ForeignKey(WalletTransaction, blank=False, null=False, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)

    # withdrawal payment choices
    _withdrawal_payment_choices = {
        0: 'E-Wallet',
        1: 'FNB/RMB',
        2: 'ABSA',
        3: 'Capitec',
        4: 'Nedbank Limted',
        5: 'Standard Bank',
        6: 'TymeBank',
        7: 'African Bank',
        8: 'Bank Zero',
        9: 'CitieBank',
        10: 'Bidvest Bank',
        11: 'VBS Mutual Bank',
        12: 'Mercantile Bank',
        13: 'HSBC Bank',
        14: 'Albaraka Bank',
        15: 'BNP Paribas',
    }

    withdrawal_payment_choices = (
        'eWallet',
        'FNB_RMB',
        'ABSA',
        'Capitec',
        'Nedbank',
        'StandardBank',
        'TymeBank',
        'AfricanBank',
        'BankZero',
        'CitieBank',
        'BidvestBank',
        'VBSMutualBank',
        'MercantileBank',
        'HSBCBank',
        'AlbarakaBank',
        'BNPParibas',
    )

    WITHDRAWAL_PAYMENT_TYPE = namedtuple('WITHDRAWAL_PAYMENT_TYPE', withdrawal_payment_choices)(*range(0, len(withdrawal_payment_choices)))
    withdrawal_payment = models.PositiveIntegerField(null=True, blank=True, choices=get_field_choices(WITHDRAWAL_PAYMENT_TYPE))
    
    # withdrawal payment choices
    _withdrawal_payment_account_type_choices = {
        0: 'Cheque Account',
        1: 'Savings Account',
        2: 'Transmission Account',
        3: 'Credit Card Account',
        4: 'Bond Account',
        5: 'Subscription Account',
    }

    withdrawal_payment_account_type_choices = (
        'Cheque',
        'Savings',
        'Transmission',
        'CreditCard',
        'Bond',
        'Subscription',
    )
    WITHDRAWAL_PAYMENT_ACCOUNT_TYPE = namedtuple('WITHDRAWAL_PAYMENT_ACCOUNT_TYPE', withdrawal_payment_account_type_choices)(*range(0, len(withdrawal_payment_account_type_choices)))
    withdrawal_payment_account = models.PositiveIntegerField(null=True, blank=True, choices=get_field_choices(WITHDRAWAL_PAYMENT_ACCOUNT_TYPE))
    
    withdrawal_account_number = models.CharField(max_length=255, null=True, blank=True)
    withdrawal_cell_number = models.CharField(max_length=255, null=True, blank=True)
    withdrawal_reference = models.CharField(max_length=255, null=True, blank=True)
  
    status_choices = (
        'Processing',
        'Completed',
        'Cancelled',
        'Reversed',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))
    status_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}. {} - {}".format(self.id, self.withdrawal_reference, self.wallet_transaction.transaction.reference)

    def save(self, *args, **kwargs):
        
        if self.withdrawal_payment is None:
            raise ValidationError('Withdrawal type is required')

        if self.withdrawal_payment == 0:
            if self.withdrawal_cell_number is None:
                raise ValidationError('E-wallet cell number is required')
        else:
            if self.withdrawal_account_number is None:
                raise ValidationError('Account number is required')
            
        super(WithdrawalWalletTransaction, self).save(*args, **kwargs)