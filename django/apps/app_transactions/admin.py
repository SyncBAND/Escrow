from django.contrib import admin

from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Transaction

admin.site.register(Transaction, TransactionAdmin)

