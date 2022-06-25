from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from collections import namedtuple
from versatileimagefield.fields import VersatileImageField, PPOIField

from apps.utils.models import CreatedModifiedMixin, PermissionsMixin
from apps.utils.views import get_field_choices, pf_payment_data

import requests


def payment_gateway_logo_upload_to(instance, filename):
    return 'nikanika/app_payment_gateway_logo/{0}/{1}'.format(instance.name, filename)
    
 
class PaymentGateway(CreatedModifiedMixin, PermissionsMixin):

    name = models.CharField(max_length=128, unique=True)
    api = models.TextField(null=True, blank=True)
    merchant_key = models.TextField(null=True, blank=True)

    payment_gateway_choices = (
        'Active',
        'Deactivated',
        'Deleted',
    )
    STATUS = namedtuple('STATUS', payment_gateway_choices)(*range(0, len(payment_gateway_choices)))
    payment_gateway_status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS))

    card_payment = models.BooleanField(default=False)

    redirect = models.BooleanField(default=False)
    redirect_url = models.URLField(null=True, blank=True)
    request_redirect_url = models.BooleanField(default=False, help_text='Request the redirect url from the payment gateway provider')

    url_interactions = models.PositiveIntegerField(default=0)

    logo = VersatileImageField(
        'Image',
        upload_to=payment_gateway_logo_upload_to,
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    is_wallet = models.BooleanField(default=False, help_text='Make sure this is the selected ONLY for the apps wallet')

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.redirect and not self.request_redirect_url:
            if not self.redirect_url or self.redirect_url == '':
                raise ValidationError('Redirect url is required')
        return super(PaymentGateway, self).save(*args, **kwargs)

    @classmethod
    def get_queryset(cls, user):
        if not user.is_authenticated:
            return PaymentGateway.objects.none()

        return PaymentGateway.objects.all()

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

    def make_payment(self, transaction=None, return_url=''):

        if not transaction:
            raise ValidationError('Transaction is required')
        
        if self.name == 'Airbuy':

            data = {
                "id": transaction.reference,
                "api_key": self.api,
                "type": "payment",
                "currency": "R",
                "total_amount": transaction.amount,
                "items": transaction.details,
                "return_method": "POST",
                "return_url": return_url
            }

            try:
                response =  requests.post(self.redirect_url, data=data, timeout=5)
                
                if int(response.status_code) != 200:
                    if 'message' in response.json():
                        if 'Payment with same ID is already completed' in response.json()['message']:
                            try:
                                data = {
                                    'id': transaction.reference,
                                    'success': 'True',
                                    'message': 'Payment successful',
                                    'datetime': response.json()['datetime'],
                                    'status_code': 200
                                }
                                response =  requests.post(transaction.notify_url, data=data, timeout=5)
                                return {
                                    'redirect': False,
                                    'url': '',
                                }
                            except Exception as e:
                                print(e)

                    transaction.logs = ("{}\n\n{} - Error: {}".format(transaction.logs, timezone.localtime(timezone.now()), str(response.content)))
                    transaction.save()
                    raise ValidationError("Airbuy: An error has occurred")

            except Exception as e:
                transaction.logs = "{}\n\n{} - Error: {}".format(transaction.logs, timezone.localtime(timezone.now()), str(e))
                transaction.save()
                raise ValidationError(e)

            if 'complete_payment_url' in response.json():
                url = response.json()['complete_payment_url']
                transaction.redirect_url = url
                transaction.save()
            else:
                raise ValidationError("complete payment url was not found")

            return {
                    'redirect': True,
                    'url': url,
                }

        elif self.name == 'Payfast':

            data = pf_payment_data(
                merchant_id=str(str(self.api)),
                merchant_key=str(self.merchant_key),
                return_url=str(transaction.return_url),
                cancel_url=str(transaction.cancel_url),
                notify_url=str(transaction.notify_url),
                name_first='',
                name_last='',
                email_address=str(transaction.payer.email),
                m_payment_id=str(transaction.reference),
                amount=str(transaction.amount),
                item_name=str(transaction.details)
            )

            try:

                transaction.signature = data['signature']
                transaction.payload_request = data
                
                try:
                    response = requests.post(self.redirect_url, data=data, timeout=5)
                except Exception as e:
                    if type(e) == requests.exceptions.ConnectionError:
                        transaction.logs = ("{}\n\n{} - Error: {}".format(transaction.logs, timezone.localtime(timezone.now()), 'Payfast: network failed. Please check connection'))
                        transaction.save()
                        raise ValidationError("Payfast: network failed. Please check connection")
                    else:
                        transaction.logs = ("{}\n\n{} - Error: {}".format(transaction.logs, timezone.localtime(timezone.now()), str(e)))
                        transaction.save()
                        raise ValidationError(e)
                
                if int(response.status_code) != 200:
                    transaction.logs = ("{}\n\n{} - Error: {}".format(transaction.logs, timezone.localtime(timezone.now()), str(response.content)))
                    transaction.save()
                    raise ValidationError("Payfast: An error has occurred")

                url = response.url
                transaction.redirect_url = url
                transaction.save()

            except Exception as e:
                transaction.logs = ("{}\n\n{} - Error: {}".format(transaction.logs, timezone.localtime(timezone.now()), e))
                transaction.save()
                raise ValidationError(e)
            
            return {
                'redirect': True,
                'url': url,
            }

        return {
                'card_payment': self.card_payment,
                'redirect': self.redirect,
                'url': self.redirect_url,
            }

    
class PaymentChargeFee(CreatedModifiedMixin, PermissionsMixin):

    percentage = models.DecimalField(max_digits=3, decimal_places=2, unique=True)
    flat_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    minimum = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    maximum = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.percentage)

    @classmethod
    def get_queryset(cls):

        return PaymentChargeFee.objects.all()