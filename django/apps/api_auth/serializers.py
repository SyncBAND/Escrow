from django.contrib.auth import get_user_model, login
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site

from apps.utils.notifications import mail_notifier
from apps.user_profile.models import UserProfile, UserSessions

from versatileimagefield.serializers import VersatileImageFieldSerializer


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=get_user_model().objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'cell', 'password', 'password2', 'email', 'first_name', 'group')
        extra_kwargs = {
            'first_name': {'required': True},
            'cell': {'required': True}
        }
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        
        with transaction.atomic():

            try:

                user = get_user_model().objects.create(
                    cell=validated_data['cell'],
                    email=validated_data['email'],
                    first_name=validated_data['first_name'],
                    is_active=True,
                    group=validated_data['group']
                )

                user.set_password(validated_data['password'])
                user.save()

                profile = UserProfile.objects.create(user=user)
                UserSessions.objects.create(profile=profile)
                
                #celery
                mail_notifier.delay(user.id, get_current_site(self.context['request']).domain, origin="apps.api_auth.serializers.RegisterSerializer", verification_type=2, subject='Verifying email address', sign_off='Take care', email_to=validated_data['email'])
                                
                return user

            except Exception as e:
                raise serializers.ValidationError(e)


class RegisterViewSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=get_user_model().objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'cell', 'password', 'password2', 'email', 'first_name', 'group')
        extra_kwargs = {
            'first_name': {'required': True},
            'cell': {'required': True}
        }
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        
        with transaction.atomic():
            try:
                user = get_user_model().objects.create(
                    cell=validated_data['cell'],
                    email=validated_data['email'],
                    first_name=validated_data['first_name'],
                    is_active=True,
                    group=validated_data['group']
                )

                user.set_password(validated_data['password'])
                user.save()

                #celery
                mail_notifier.delay(user.id, get_current_site(self.context['request']).domain, origin="apps.api_auth.serializers.RegisterSerializer", verification_type=2, subject='Verifying email address', sign_off='Take care', email_to=validated_data['email'])
                
                login(self.context['request'], user)

                return user

            except Exception as e:
                raise serializers.ValidationError(e)


class UserSerializer(serializers.ModelSerializer):

    avatar = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    
    profile_pic = serializers.SerializerMethodField()
    share_code = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'avatar', 'cell', 'email', 'first_name', 'last_name', 'get_full_name', 'is_email_verified', 'profile_pic', 'share_code')
        read_only_fields = ('id', )

    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        return

    def get_share_code(self, obj):
        try:
            return UserProfile.objects.get(user=obj.id).share_code
        except Exception as e:
            return ''
        
    def get_profile_pic(self, obj):
        if obj.avatar:
            request = self.context.get('request', None)
            if request:
                return request.build_absolute_uri(obj.avatar.url)

        return 'https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-alt-512.png'