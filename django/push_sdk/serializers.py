from rest_framework import serializers

from .models import PushDevice


class PushDeviceSerializer(serializers.ModelSerializer):

    platform_ = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()

    class Meta:
        model = PushDevice
        fields = ('id', 'user', 'name', 'resend_counter', 'registration_id', 'app_version', 'platform', 'platform_')
    
    def create(self, validate_data):

        registration_id = self.context['request'].data.get('registration_id', None)
        platform = self.context['request'].data.get('platform', 'ANDROID').upper()
        name = self.context['request'].data.get('name', platform)

        user = self.context['request'].user
        
        try:
            app_version = self.context['request'].data.get('app_version', '0.0.1')
            app_version = int( app_version.replace('.', '') )
        except:
            app_version = None

        try:
            device = PushDevice.objects.select_related().get(active=True, user=user, registration_id=registration_id)
            device.app_version = app_version
            device.name = name
            device.platform = PushDevice.PLATFORM_DICT[platform]
            device.save()
        except:
            PushDevice.objects.filter(active=True, user=user).update(active=False)
            device = PushDevice.objects.create(active=True, user=user, registration_id=registration_id, platform = PushDevice.PLATFORM_DICT[platform], app_version = app_version, name = name)
        
        return device
    
    def get_platform_(self, obj):

        return PushDevice._platform[obj.platform]
    
    def get_platform(self, obj):

        return PushDevice._platform[obj.platform]