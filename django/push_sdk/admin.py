from django.contrib import admin

from .models import PushDevice

class PushDeviceAdmin(admin.ModelAdmin):
    list_display = ["__str__", 'active', 'created', 'modified']
    class Meta:
        model = PushDevice
admin.site.register(PushDevice, PushDeviceAdmin)