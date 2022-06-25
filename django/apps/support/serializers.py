from django.db import transaction

from rest_framework import serializers

from versatileimagefield.serializers import VersatileImageFieldSerializer

from apps.support.models import Support, SupportActivity
from apps.api_auth.serializers import UserSerializer


class SupportSerializer(serializers.ModelSerializer):
    
    image_1 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_2 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_3 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_4 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_5 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_6 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_7 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_8 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )

    images = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Support
        fields = ('id', 'title', 'description', 'problem', 'user', 'user_details', 'status', 'status_details', 'latitude', 'longitude', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6', 'image_7', 'image_8', 'images', 'current_status', 'created', 'modified', 'location', 'city', 'province', 'country')


    def create(self, validated_data):
        
        try:
            with transaction.atomic():
                if self.context['request'].user.is_authenticated:
                    validated_data['user'] = self.context['request'].user

                    return Support.objects.create(**validated_data)
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        

    def update(self, instance, validated_data):
        
        try:
            with transaction.atomic():

                if self.context['request'].user.is_authenticated:
                    if self.context['request'].user == instance.user or self.context['request'].user.is_superuser:
                        instance.save()
                    else:
                        raise serializers.ValidationError('User not permitted')
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return instance

    
    def get_user_details(self, obj):
        return UserSerializer(obj.user, context=self.context).data

    def get_current_status(self, obj):
        return Support.status_choices[obj.status]

    def get_images(self, obj):
        
        image_list = []

        if obj.image_1:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_1.url)))

        if obj.image_2:
            request = self.context['request']
            if request:
                
                image_list.append(str(request.build_absolute_uri(obj.image_2.url)))

        if obj.image_3:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_3.url)))

        if obj.image_4:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_4.url)))

        if obj.image_5:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_5.url)))

        if obj.image_6:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_6.url)))

        if obj.image_7:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_7.url)))

        if obj.image_8:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_8.url)))

        return image_list

class SupportActivitySerializer(serializers.ModelSerializer):

    image_1 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_2 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_3 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_4 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_5 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_6 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_7 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_8 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )

    images = serializers.SerializerMethodField()

    previous_status_ = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = SupportActivity
        fields = ('id', 'support_id', 'user', 'current_status', 'previous_status', 'previous_status_', 'previous_status_details', 'status', 'status_details', 'latitude', 'longitude', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6', 'image_7', 'image_8', 'images', 'created', 'modified', 'location', 'city', 'province', 'country')

    def create(self, validated_data):

        try:

            with transaction.atomic():

                request = self.context['request']
                user = request.user
                body = self.context['request']
                data = request.data

                support_id = request.data.get('support_id', 0)
                support = Support.objects.get(id=support_id)
                
                status = SupportActivity._status_choices[data['current_status']]

                validated_data['user'] = user
                validated_data['status'] = status
                validated_data['previous_status'] = support.status
                validated_data['previous_status_details'] = support.status_details

                if support.status == int(status):
                    raise serializers.ValidationError('Support is already ' + str(Support.STATUS_TYPE[status]) + '. Nothing to be done.')
            
                elif support.status == Support.STATUS_TYPE.Deleted:
                    raise serializers.ValidationError('Support is deleted. Nothing to be done.')

                else:
                    support.status = status

                support.status_details = validated_data['status_details']
                support.save()

                validated_data['support'] = support
                instance =  SupportActivity.objects.create(**validated_data)

                return instance

        except Exception as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        return
    
    def get_previous_status_(self, obj):
        return SupportActivity.previous_status_choices[obj.previous_status]
    
    def get_current_status(self, obj):
        return SupportActivity.status_choices[obj.status]

    def get_images(self, obj):
        
        image_list = []

        if obj.image_1:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_1.url)))

        if obj.image_2:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_2.url)))

        if obj.image_3:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_3.url)))

        if obj.image_4:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_4.url)))

        if obj.image_5:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_5.url)))

        if obj.image_6:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_6.url)))

        if obj.image_7:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_7.url)))

        if obj.image_8:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_8.url)))

        return image_list