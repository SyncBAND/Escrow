from rest_framework import serializers

from apps.app_transactions.models import Transaction
from apps.api_auth.serializers import UserSerializer
from apps.app_payment_gateway.serializers import PaymentGatewayShortSerializer


class TransactionSerializer(serializers.ModelSerializer):

    payment_gateway_selected = serializers.SerializerMethodField()
    payer = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    s_type = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    transaction_uri = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'payer', 'payment_gateway_selected', 'recipient', 'reference', 'share_code', 'amount', 'original_amount', 'calculated_charge', 'percentage_charge', 'flat_fee', 'signature', 'pf_m_payment_id', 'pf_payment_id', 'pf_payment_status', 'pf_item_name', 'pf_item_description', 'pf_amount_gross', 'pf_amount_fee', 'pf_amount_net', 'payload_request', 'payload_response', 'status', 'goods_delivered', 'goods_delivered_details', 'rating', 'withdrawn', 'details', 'logs', 'refund', 'withdrawal_status', 's_type', 'current_status', 'color', 'created', 'modified', 'transaction_uri')
        read_only_fields = ('id', 'share_code', 'payment_gateway_selected', 'reference', 'signature', 'pf_m_payment_id', 'pf_payment_id', 'pf_payment_status', 'pf_item_name', 'pf_item_description', 'pf_amount_gross', 'pf_amount_fee', 'pf_amount_net', 'payload_request', 'payload_response', 'goods_delivered', 'goods_delivered_details', 'rating', 'withdrawn', 'logs', 'withdrawal_status', 'created', 'modified')

    def get_transaction_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/transactions/{id}/".format(id=obj.id))
    
    def get_payer(self, obj):
        return UserSerializer(obj.payer, context=self.context).data
        
    def get_recipient(self, obj):
        return UserSerializer(obj.recipient, context=self.context).data
        
    def get_payment_gateway_selected(self, obj):
        return PaymentGatewayShortSerializer(obj.payment_gateway, context=self.context).data

    def create(self, validate_data):
        
        user = self.context['request'].user
        if user.is_authenticated:
            return Transaction.objects.create(**validate_data)
    
        raise serializers.ValidationError('User needs to be signed in')

    def update(self, instance, validated_data):
        return 

    def get_s_type(self, obj):

        return Transaction.status_choices[obj.status]
    
    def get_current_status(self, obj):

        return Transaction._STATUS_TYPE[obj.status]
    
    def get_color(self, obj):

        return Transaction._COLOR_TYPE[obj.status]