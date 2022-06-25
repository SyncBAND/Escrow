from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from apps.wallet_transactions.models import WalletTransaction, WithdrawalWalletTransaction
from apps.app_transactions.serializers import TransactionSerializer
from apps.api_auth.serializers import UserSerializer


class WalletTransactionSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField(read_only=True)
    transaction = serializers.SerializerMethodField(read_only=True)
    wallet_transaction_uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WalletTransaction
        fields = ('id', 'user_profile', 'user', 'transaction', 'wallet_reference', 'previous_wallet_amount', 'transaction_amount', 'wallet_transaction', 'transaction_details',  'created', 'modified', 'wallet_transaction_uri')
        read_only_fields = ('id', 'user_profile', 'wallet_reference', 'previous_wallet_amount')
    
    def get_transaction(self, obj):
        return TransactionSerializer(obj.transaction, context=self.context).data

    def get_user(self, obj):
        return UserSerializer(obj.user_profile.user, context=self.context).data

    def get_wallet_transaction_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/enterprise/client-wallet-transactions/{id}/".format(id=obj.id))
                
    def create(self, validated_data):
        raise serializers.ValidationError('User not permitted to create wallet transactions')

    def update(self, instance, validated_data):

        raise serializers.ValidationError('User not permitted to update wallet transactions')



class WithdrawalWalletTransactionSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField(read_only=True)
    status_choices = serializers.SerializerMethodField(read_only=True)
    withdrawal_payment_choices = serializers.SerializerMethodField(read_only=True)
    withdrawal_payment_account_type_choices = serializers.SerializerMethodField(read_only=True)
    withdrawal_wallet_transaction_uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WithdrawalWalletTransaction
        fields = ('id', 'wallet_transaction', 'user', 'amount', 'withdrawal_payment', 'withdrawal_payment_account', 'withdrawal_account_number', 'withdrawal_cell_number', 'withdrawal_reference', 'status', 'status_choices', 'status_details', 'withdrawal_payment_choices', 'withdrawal_payment_account_type_choices', 'withdrawal_wallet_transaction_uri', 'created', 'modified')
        read_only_fields = ('id', 'wallet_transaction')
    
    def get_withdrawal_wallet_transaction_uri(self, obj):
        return self.context['request'].build_absolute_uri("/api/wallet-transactions/{id}/".format(id=obj.id))
    
    def get_user(self, obj):
        return UserSerializer(obj.wallet_transaction.user_profile.user, context=self.context).data

    def get_status_choices(self, obj):
        return WithdrawalWalletTransaction.status_choices[obj.status]
    
    def get_withdrawal_payment_choices(self, obj):
        if obj.withdrawal_payment is not None:
            return WithdrawalWalletTransaction._withdrawal_payment_choices[obj.withdrawal_payment]
        return 0

    def get_withdrawal_payment_account_type_choices(self, obj):
        return WithdrawalWalletTransaction._withdrawal_payment_account_type_choices[obj.withdrawal_payment_account]
                
    def create(self, validated_data):
        
        raise serializers.ValidationError('User not permitted to create wallet transactions')

    def update(self, instance, validated_data):

        raise serializers.ValidationError('User not permitted to update wallet transactions')