from rest_framework import serializers

from .models import PaymentChargeFee, PaymentGateway

from versatileimagefield.serializers import VersatileImageFieldSerializer


class PaymentGatewayShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentGateway
        fields = ('id', 'name', 'payment_gateway_status', 'logo', 'is_wallet')
        read_only_fields = ('id', )

    def create(self, validate_data):
        return
    def update(self, validate_data):
        return

class PaymentGatewaySerializer(serializers.ModelSerializer):

    logo = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    payment_gateway_uri = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGateway
        fields = ('id', 'name', 'api', 'payment_gateway_status', 'redirect', 'redirect_url', 'request_redirect_url', 'logo', 'is_wallet', 'payment_gateway_uri')
        read_only_fields = ('id', )

    def get_payment_gateway_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/app-payment-gateway/{id}/".format(id=obj.id))
    
    def create(self, validate_data):
        try:
            user = self.context['request'].user

            if user.is_authenticated:
                if user.is_superuser or user.is_staff:
                    return PaymentGateway.objects.create(**validate_data)
        
            raise serializers.ValidationError('User is not permitted.')
            
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):

        user = self.context['request'].user
        if user.is_authenticated:

            if user.is_superuser or user.is_staff:

                for attr, value in validated_data.items():
                    setattr(instance, attr, value)

                return instance.save()
    
        raise serializers.ValidationError('User is not permitted.')

    def get_m_type(self, obj):
        return PaymentGateway._STATUS_TYPE[obj.type]
    
    def get_current_status(self, obj):
        return PaymentGateway.status_choices[obj.status]
    

class PaymentChargeFeeSerializer(serializers.ModelSerializer):

    payment_charge_fee_uri = serializers.SerializerMethodField()

    class Meta:
        model = PaymentChargeFee
        fields = ('id', 'percentage', 'flat_fee', 'minimum', 'maximum', 'payment_charge_fee_uri')

    def create(self, validate_data):
        
        user = self.context['request'].user
        if user.is_authenticated:

            if user.is_superuser or user.is_staff:
                return PaymentGateway.objects.create(**validate_data)
    
        raise serializers.ValidationError('User is not permitted.')

    def update(self, instance, validated_data):
        
        user = self.context['request'].user
        if user.is_authenticated:

            if user.is_superuser or user.is_staff:

                for attr, value in validated_data.items():
                    setattr(instance, attr, value)

                return instance.save()
    
        raise serializers.ValidationError('User is not permitted.')

    def get_payment_charge_fee_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/app-payment-charge-fee/{id}/".format(id=obj.id))