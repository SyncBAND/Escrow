from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.api_messages.models import Message, MessageCleanUp, MessageResend, MessageTasks

class MessageAdmin(admin.ModelAdmin):
    
    class Meta:
        model = Message
        
    search_fields = [
        'id',
        'recipients',
        'message',
        'origin',
        'remote_message_status',
        'status',
        'type',
        'remote_id'
    ]
    list_display = (
        'id',
        'recipients',
        'message',
        'origin',
        'remote_message_status',
        'status',
        'type',
    )
    actions = ('terminate_active_tasks', )

    def terminate_active_tasks(self, request, queryset):
        for message in queryset:
            try:
                result = message.terminate_active_tasks(request.user)
                self.message_user(request, "Termination result - {}".format(result))
            except Exception as e:
                self.message_user(request, "Termination Error ID: {} - {}".format(message.id, e))

    terminate_active_tasks.short_description = _("Terminate active sending tasks")

admin.site.register(Message, MessageAdmin)

class MessageTasksAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = MessageTasks

admin.site.register(MessageTasks, MessageTasksAdmin)

class MessageResendAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = MessageResend

admin.site.register(MessageResend, MessageResendAdmin)

class MessageCleanUpAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = MessageCleanUp

admin.site.register(MessageCleanUp, MessageCleanUpAdmin)