from django.contrib import admin

from .models import WalletTransaction, WithdrawalWalletTransaction

class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = WalletTransaction

admin.site.register(WalletTransaction, WalletTransactionAdmin)

class WithdrawalWalletTransactionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "status"]
    class Meta:
        model = WithdrawalWalletTransaction

admin.site.register(WithdrawalWalletTransaction, WithdrawalWalletTransactionAdmin)