from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from .models import PaymentGateway, PaymentChargeFee

class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = PaymentGateway

    def save_model(self, request, obj, form, change):

        try:
            return super().save_model(request, obj, form, change)
        except Exception as e:
            return self.message_user(
				request, e,
				level=messages.ERROR
			)

    def response_change(self, request, obj):

        if obj.redirect:
            if not obj.redirect_url or obj.redirect_url == '':
                return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        
        if obj.redirect:
            if not obj.redirect_url or obj.redirect_url == '':
                return HttpResponseRedirect(request.path)
        
        return super().response_add(request, obj, post_url_continue)

admin.site.register(PaymentGateway, PaymentGatewayAdmin)


class PaymentChargeFeeAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = PaymentChargeFee

admin.site.register(PaymentChargeFee, PaymentChargeFeeAdmin)
