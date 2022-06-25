from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum
from django.db import transaction
from django.conf import settings

from versatileimagefield.serializers import VersatileImageFieldSerializer

from rest_framework import serializers

from apps.user_profile.models import UserProfile, UserVerifiedProfileCase
from apps.app_transactions.models import Transaction
from apps.api_auth.serializers import UserSerializer
from apps.utils.notifications import email_update_notifier


class UserVerifiedProfileCaseSerializer(serializers.ModelSerializer):
    
    user_verified_profile_case_uri = serializers.SerializerMethodField()

    class Meta:
        model = UserVerifiedProfileCase
        fields = ('id', 'profile', 'creator', 'details', 'status', 'user_verified_profile_case_uri')
        read_only_fields = ('id', 'share_code')

    def get_user_verified_profile_case_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/user-verified-profile-case/{id}/".format(id=obj.id))


class UserProfileSerializer(serializers.ModelSerializer):

    user_details = serializers.SerializerMethodField()

    money_recieved = serializers.SerializerMethodField()
    money_paid = serializers.SerializerMethodField()

    identification_choices = serializers.SerializerMethodField()
    account_type_choices = serializers.SerializerMethodField()
    verified_details_status_choices = serializers.SerializerMethodField()
    user_verified_profile_case = serializers.SerializerMethodField()

    withdrawal_payment_choices = serializers.SerializerMethodField(read_only=True)
    withdrawal_payment_account_type_choices = serializers.SerializerMethodField(read_only=True)

    withdrawal_payment_options = serializers.SerializerMethodField()
    withdrawal_payment_account_type_options = serializers.SerializerMethodField()
    
    user_id = serializers.SerializerMethodField()
    
    user_profile_uri = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'user_details', 'wallet', 'share_code', 'location', 'latitude', 'longitude', 'email', 'verified_email', 'verified_details', 'verified_details_status', 'date_email_verified', 'verified_cell', 'id_number', 'identification', 'identification_choices', 'account_type', 'account_type_choices', 'verified_details_status_choices', 'barcoded_id', 'front_smart_id', 'back_smart_id', 'passport_id', 'certified_copy', 'picture_with_id', 'proof_of_address', 'company_registration', 'company_proof_of_residence', 'money_recieved', 'money_paid', 'user_verified_profile_case', 'withdrawal_payment', 'withdrawal_payment_account', 'withdrawal_account_number', 'withdrawal_cell_number', 'withdrawal_reference', 'withdrawal_payment_choices', 'withdrawal_payment_account_type_choices', 'withdrawal_payment_options', 'withdrawal_payment_account_type_options', 'user_id', 'user_profile_uri', 'created', 'modified')
        read_only_fields = ('id', 'wallet', 'share_code', 'user_details', 'account_type_choices', 'verified_details_status_choices', 'identification_choices', 'verified_details_status', 'user_profile_uri', 'account_type', 'withdrawal_payment_options', 'withdrawal_payment_account_type_options', 'identification', 'created', 'modified')

    def get_user_profile_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/user-profiles/{id}/".format(id=obj.id))
    
    def get_withdrawal_payment_choices(self, obj):
        if obj.withdrawal_payment:
            return UserProfile._withdrawal_payment_choices[obj.withdrawal_payment]
        return 0
    
    def get_withdrawal_payment_options(self, obj):
        return UserProfile.withdrawal_payment_choices
    
    def get_withdrawal_payment_account_type_choices(self, obj):
        return UserProfile._withdrawal_payment_account_type_choices[obj.withdrawal_payment_account]
    
    def get_withdrawal_payment_account_type_options(self, obj):
        return UserProfile.withdrawal_payment_account_type_choices

    def get_money_recieved(self, obj):
        try:
            return 'R{}'.format(round( Transaction.objects.filter(recipient=obj.user, status=Transaction.STATUS_TYPE.Complete).aggregate(Sum('original_amount'))['original_amount__sum'], 2 ))
        except:
            return 'R0.00'

    def get_money_paid(self, obj):
        try:
            return 'R{}'.format(round( Transaction.objects.filter(payer=obj.user, status=Transaction.STATUS_TYPE.Complete).aggregate(Sum('amount'))['amount__sum'], 2 ))
        except Exception as e:
            return 'R0.00'
    
    def get_user_verified_profile_case(self, obj):
        try:
            return [UserVerifiedProfileCaseSerializer(case, context=self.context).data for case in UserVerifiedProfileCase.objects.filter(profile=obj, status=0)]
        except Exception as e:
            return []
    
    def get_user_details(self, obj):
        try:
            return UserSerializer(obj.user, context=self.context).data
        except:
            return []
    
    def get_identification_choices(self, obj):
        try:
            return UserProfile.identification_choices[obj.identification]
        except:
            return 'barcode'
    
    def get_account_type_choices(self, obj):
        try:
            return UserProfile.account_type_choices[obj.account_type]
        except:
            return 'individual'
    
    def get_verified_details_status_choices(self, obj):
        try:
            return UserProfile.verified_details_status_choices[obj.verified_details_status]
        except:
            return 'Incomplete'
    
    def get_user_id(self, obj):
        return obj.user.id

    def create(self, validated_data):
        raise serializers.ValidationError('Not permitted')

    def update(self, instance, validated_data):

        try:
            with transaction.atomic():

                validated_data['identification'] = UserProfile._identification_choices[self.context['request'].data.get('identification')]
                validated_data['account_type'] = UserProfile._account_type_choices[self.context['request'].data.get('account_type')]
                validated_data['verified_details_status'] = 1

                if(instance.user == self.context['request'].user):
                    pass
                elif self.context['request'].user.is_superuser:
                    pass
                else:
                    raise serializers.ValidationError('Not permitted to update')

                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                
                details = 'Your profile is being processed'
                
                try:
                    case = UserVerifiedProfileCase.objects.get(profile=instance, status=0)
                    case.details = details
                    case.save()
                except:
                    UserVerifiedProfileCase.objects.create(profile=instance, details = details)

                    #mail
                    email_update_notifier.delay(instance.user.id, subject='Profile is being processed', msg="Thank you for submitting your documents. Your profile is currently being processed.", origin='UserProfileSerializer.update', sign_off='The Team', email_to=instance.user.email_address)
                    
                    #mail
                    email_update_notifier.delay(instance.user.id, subject='Process profile: {}'.format(instance.user.id), msg="Process profile for user {}. {}".format(instance.user.id, instance.user.email), origin='UserProfileSerializer.update', sign_off='The Team', email_to=settings.EMAIL_HOST_USER, user_receiving_mail=1)

                instance.save()
                
                return instance

        except Exception as e:
            raise serializers.ValidationError(str(e))
 
 
class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"detail": "Password fields didn't match."})
        elif len(attrs['password']) < 5:
            raise serializers.ValidationError({"detail": "Password length cannot be less than 5 characters."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        user = self.context['request'].user

        if user.pk != instance.pk or not user.is_active:
            raise serializers.ValidationError({"detail": "You dont have permission for this action."})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(read_only=True)
    avatar = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    is_email_verified = serializers.CharField(read_only=True)
    is_cell_verified = serializers.CharField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'cell', 'first_name', 'last_name', 'email', 'avatar', 'is_email_verified', 'is_cell_verified')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        try:
            if user.pk != instance.pk or not user.is_active:
                raise serializers.ValidationError("You dont have permission for this action.")

            if get_user_model().objects.exclude(pk=user.pk).filter(cell=validated_data['cell']).exists():
                raise serializers.ValidationError("This cell is already in use.")

            if 'avatar' in validated_data:
                instance.avatar = validated_data['avatar']

            instance.first_name = validated_data['first_name']
            instance.last_name = validated_data['last_name']
            instance.cell = validated_data['cell']

            if 'email' in validated_data:
                validated_data.pop('email', None)

            instance.save()

        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})

        return instance


class DeleteUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('cell', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
        
    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk or not user.is_active:
            raise serializers.ValidationError({"detail": "You dont have permission for this action."})

        instance.is_active = False

        instance.save()
        return instance
    