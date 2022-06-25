from django.contrib import admin

from .models import Support, SupportActivity

class SupportAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Support
admin.site.register(Support, SupportAdmin)

class SupportActivityAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = SupportActivity
admin.site.register(SupportActivity, SupportActivityAdmin)

