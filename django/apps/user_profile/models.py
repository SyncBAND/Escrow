from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator

from collections import namedtuple


def user_profile_upload_to(instance, filename):
    return 'nikanika/user_profile/documents/{0}/{1}'.format(instance.id, filename)


class UserMode(CreatedModifiedMixin):

    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class UserProfile(CreatedModifiedMixin):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    wallet = models.DecimalField(max_digits=8, decimal_places=2, default=0, null=True, blank=True)

    share_code = models.CharField(max_length=128)

    location = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    verified_email = models.BooleanField(default=False)
    date_email_verified = models.DateTimeField(default=timezone.now)

    verified_cell = models.BooleanField(default=False)

    verified_details = models.BooleanField(default=False)
    verified_details_choices = (
        'Incomplete',
        'Processing',
        'Complete',
    )
    VERIFIED_DETAILS_TYPE = namedtuple('VERIFIED_DETAILS_TYPE', verified_details_choices)(*range(0, len(verified_details_choices)))
    verified_details_status = models.PositiveIntegerField(default=0, choices=get_field_choices(VERIFIED_DETAILS_TYPE))
    
    id_number = models.CharField(max_length=7, null=True, blank=True)
    api_key = models.CharField(max_length=32, null=True, blank=True)

    _identification_choices = {
        'barcode': 0,
        'smart': 1,
        'passport': 2,
    }
    identification_choices = (
        'barcode',
        'smart',
        'passport',
    )
    IDENTIFICATION_TYPE = namedtuple('IDENTIFICATION_TYPE', identification_choices)(*range(0, len(identification_choices)))
    identification = models.PositiveIntegerField(null=True, blank=True, choices=get_field_choices(IDENTIFICATION_TYPE))

    _account_type_choices = {
        'individual':0,
        'company':1,
    }
    account_type_choices = (
        'individual',
        'company',
    )
    ACCOUNT_TYPE = namedtuple('ACCOUNT_TYPE', account_type_choices)(*range(0, len(account_type_choices)))
    account_type = models.PositiveIntegerField(null=True, blank=True, choices=get_field_choices(ACCOUNT_TYPE))

    barcoded_id = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    front_smart_id = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    back_smart_id = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    passport_id = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    certified_copy = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    picture_with_id = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    proof_of_address = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    company_registration = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    company_proof_of_residence = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)

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
    withdrawal_payment_account = models.PositiveIntegerField(default=0, choices=get_field_choices(WITHDRAWAL_PAYMENT_ACCOUNT_TYPE))
    
    withdrawal_account_number = models.CharField(max_length=255, null=True, blank=True)
    withdrawal_cell_number = models.CharField(max_length=255, null=True, blank=True)
    withdrawal_reference = models.CharField(max_length=255, null=True, blank=True)
  
    # -- ratings given to enduser by agent --#
    # to get rating percentage = (total_sum_of_ratings_for_users/5)/total_number_of_ratings_for_users
    total_sum_of_ratings_for_users = models.PositiveIntegerField(default=0)
    total_number_of_ratings_for_users = models.PositiveIntegerField(default=0)
    # -- end ratings for --#

    # -- ratings from endusers given to agent --#
    # to get rating percentage = (total_sum_of_ratings_from_users/5)/total_number_of_ratings_from_users
    total_sum_of_ratings_from_users = models.PositiveIntegerField(default=0)
    total_number_of_ratings_from_users = models.PositiveIntegerField(default=0)
    # -- end ratings from --#

    def save(self, *args, **kwargs):
        
        if not self.share_code:
            while True:
                share_code = random_generator(length=6, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(share_code=share_code).only('share_code').exists():
                    break
            self.share_code = share_code

        if not self.api_key:
            while True:
                api_key = random_generator(length=32, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(share_code=api_key).only('api_key').exists():
                    break
            self.api_key = api_key


        if self.identification == UserProfile._identification_choices['barcode']:
            if not self.barcoded_id:
                raise ValidationError("Barcode ID image is required")
            
        elif self.identification == UserProfile._identification_choices['smart']:
            if not self.front_smart_id:
                raise ValidationError("Front image of smart ID is required")
    
            elif not self.back_smart_id:
                raise ValidationError("Back image of smart ID is required")
            
        elif self.identification == UserProfile._identification_choices['passport']:
            if not self.passport_id:
                raise ValidationError("Passport image is required")
            
        if self.identification:
            if not self.picture_with_id:
                    raise ValidationError("Selfie image holding up ID/Passport is required")

            elif not self.certified_copy:
                    raise ValidationError('Certified copy of ID is required')

            elif not self.proof_of_address:
                    raise ValidationError('Copy of proof of address is required')

            elif self.account_type == UserProfile._account_type_choices['company']:
                if not self.company_registration:
                    raise ValidationError('Copy of company registration is required')
                elif not self.company_proof_of_residence:
                    raise ValidationError('Copy of company proof of address is required')
        
        return super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user.first_name)

    @classmethod
    def get_queryset(cls, user):

        if not user.is_authenticated:
            return UserProfile.objects.none()
        
        if user.is_superuser or user.is_staff:
            return UserProfile.objects.all()
        
        return UserProfile.objects.filter(user=user)


class UserVerifiedProfileCase(CreatedModifiedMixin):

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)

    details = models.TextField(blank=True, null=True)

    status_choices = (
        'incomplete',
        'complete',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))

    def __str__(self):
        return self.profile.user.first_name
        
    @classmethod
    def get_queryset(cls, user):

        if not user.is_authenticated:
            return UserVerifiedProfileCase.objects.none()
        
        if user.is_superuser or user.is_staff:
            return UserVerifiedProfileCase.objects.all()
        
        return UserVerifiedProfileCase.objects.filter(profile__user=user)


class UserSessions(CreatedModifiedMixin):

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    location = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)

    ip_address = models.CharField(max_length=128, null=True, blank=True)

    # update later - keep track of time
    session_code = models.CharField(max_length=128, null=True, blank=True)

    logs = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.profile.user.first_name


class UserChanges(CreatedModifiedMixin):

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    previous_id_copy = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)
    previous_id_copy_extra = models.FileField(blank=True, null=True, upload_to=user_profile_upload_to)

    def __str__(self):
        return self.profile.user.first_name


class UserRatings(CreatedModifiedMixin):

    user_profile_making_rating = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_profile_making_rating')
    user_profile_being_rated = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_profile_being_rated')

    transaction_id = models.PositiveIntegerField(null=True, blank=True)

    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    editted = models.BooleanField(default=False)

    # because of ratings that could be from different apps - e.g support or enquiries
    # currently just enquiries
    
    def __str__(self):
        return "{} rated {}".format(str(self.user_profile_making_rating.user.first_name), str(self.user_profile_being_rated.user.first_name))


class UserRatingsHistory(CreatedModifiedMixin):

    user_ratings = models.ForeignKey(UserRatings, on_delete=models.CASCADE)

    previous_rating = models.PositiveIntegerField(default=0)
    previous_review = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} updated rating on {}".format(str(self.user_ratings.user_profile_making_rating.user.first_name), str(self.user_ratings.user_profile_being_rated.user.first_name))