from django.conf import settings
from django.db import models

from collections import namedtuple

from softdelete.models import SoftDeleteObject

from apps.app_payment_gateway.models import PaymentGateway
from apps.utils.models import CreatedModifiedMixin, PermissionsMixin
from apps.utils.views import get_field_choices, random_generator


class Transaction(CreatedModifiedMixin, PermissionsMixin, SoftDeleteObject):

    payer = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False, on_delete=models.CASCADE, related_name='transaction_payer')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False, on_delete=models.CASCADE, related_name='transaction_recipient')

    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)

    reference = models.CharField(max_length=256, blank=True, null=True, unique=True)
    share_code = models.CharField(max_length=256, blank=True, null=True)

    amount = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    original_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    calculated_charge = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    percentage_charge = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    flat_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    signature = models.CharField(max_length=512, blank=True, null=True)

    pf_m_payment_id = models.CharField(max_length=512, blank=True, null=True)
    pf_payment_id = models.CharField(max_length=512, blank=True, null=True)
    pf_payment_status = models.CharField(max_length=512, blank=True, null=True)
    pf_item_name = models.CharField(max_length=512, blank=True, null=True)
    pf_item_description = models.CharField(max_length=512, blank=True, null=True)
    pf_amount_gross = models.CharField(max_length=512, blank=True, null=True)
    pf_amount_fee = models.CharField(max_length=512, blank=True, null=True)
    pf_amount_net = models.CharField(max_length=512, blank=True, null=True)

    # data sent
    payload_request = models.JSONField(blank=True, null=True)
    # data response
    payload_response = models.JSONField(blank=True, null=True)

    refund = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    details = models.TextField(default='', blank=True, null=True)
    cancellation_reason = models.TextField(default='', blank=True, null=True)

    goods_delivered = models.BooleanField(default=False)
    goods_delivered_details = models.TextField(blank=True, null=True)
    withdrawn = models.BooleanField(default=False)
    # from WithdrawalWalletTransaction
    # status_choices = (
    #     'Processing',
    #     'Completed',
    #     'Cancelled',
    #     'Reversed',
    # )
    withdrawal_status = models.PositiveIntegerField(blank=True, null=True)
    rating = models.PositiveIntegerField(blank=True, null=True) # by payer
    
    logs = models.TextField(default='', blank=True, null=True)

    redirect_url = models.URLField(blank=True, null=True)
    return_url = models.URLField(blank=True, null=True)
    notify_url = models.URLField(blank=True, null=True)
    cancel_url = models.URLField(blank=True, null=True)

    _COLOR_TYPE = {
        0: '#0000FF',
        1: '#FFA500',
        2: '#008000',
        3: '#FF0000',
        4: '#808080'
    }
    _STATUS_TYPE = {
        0: 'Initiated',
        1: 'Pending',
        2: 'Complete',
        3: 'Cancelled',
        4: 'Refund'
    }
    status_choices = (
        'Initiated',
        'Pending',
        'Complete',
        'Cancelled',
        'Refund',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))

    def __str__(self):
        return "{}. {}".format(self.id, self.reference)

    def save(self, *args, **kwargs):

        if not self.reference:
            while True:
                reference = random_generator(length=9, letters=True, digits=True, punctuation=False, exclude=[])
                if not type(self).objects.filter(reference=reference).exists():
                    break
            self.reference = reference

        return super(Transaction, self).save(*args, **kwargs)

    @classmethod
    def get_queryset(cls, user):

        if not user.is_authenticated:
            return Transaction.objects.none()

        if user.is_superuser or user.is_staff:
            return Transaction.objects.all()

        return Transaction.objects.filter(models.Q(payer=user) | models.Q(recipient=user))

    @classmethod
    def has_permission(cls, request):
        """ 
        Permissions for Privileged users.
        """

        if request.user.is_authenticated:
            return True

        return False

    def has_object_permission(self, request, obj):
        """ 
        Object Permissions for Privileged users.
        """

        if request.user.is_authenticated:
            return True
        
        return False