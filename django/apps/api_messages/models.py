from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core import management

from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices

from collections import namedtuple

 
class Message(CreatedModifiedMixin):
    
    CONSTANCE = {
        'FCM_API_KEY':'AIzaSyDTfKkIBfSjhezsoKu0HXINAAqCjRriXWc',
        'PUSH_TTL':0,
        'PUSH_PRIORITY_ANDROID':'normal',
        'PUSH_PRIORITY_IOS':5,
        'PUSH_PRIORITY_VALUE':10,
        'PUSH_RESEND_INTERVAL_IN_MINUTES':60,
        'CELERY_HIGH_PRIORITY': 9,
        'CELERY_MEDIUM_PRIORITY': 6,
        'CELERY_LOW_PRIORITY': 3,
        'MESSAGE_DELIVERED':0,
        'MESSAGE_UNDELIVERED':1,
        'MESSAGE_QUEUED_AT_NETWORK':2,
        'MESSAGE_SENT_TO_NETWORK':3,
        'MESSAGE_FAILED_AT_NETWORK':4,
        'MESSAGE_DOES_NOT_EXIST':5,
        'MESSAGE_BLOCKED_OR_DELETED':6
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    subject = models.CharField(max_length=128, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    
    recipients = models.TextField(null=True, blank=True)

    origin = models.TextField(blank=True, null=True)

    remote_id = models.TextField(blank=True, null=True)
    remote_message_status = models.CharField(max_length=128, blank=True, null=True)

    _type = (
        'SMS',
        'PUSH_NOTIFICATION',
        'EMAIL',
    )
    MESSAGE_TYPE = namedtuple('MESSAGE_TYPE', _type)(*range(0, len(_type)))
    type = models.PositiveIntegerField(default=2, choices=get_field_choices(MESSAGE_TYPE))

    status_choices = (
        'MESSAGE_DELIVERED',
        'MESSAGE_UNDELIVERED',
        'MESSAGE_QUEUED_AT_NETWORK',
        'MESSAGE_SENT_TO_NETWORK',
        'MESSAGE_FAILED_AT_NETWORK',
        'MESSAGE_DOES_NOT_EXIST',
        'MESSAGE_BLOCKED_OR_DELETED'
    )
    TYPE = namedtuple('TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=1, choices=get_field_choices(TYPE))
    status_response = models.TextField(null=True, blank=True)

    user_receiving_mail_choices = (
        'user',
        'admin_or_staff'
    )
    USER_RECEIVING_MAIL_TYPE = namedtuple('USER_RECEIVING_MAIL_TYPE', user_receiving_mail_choices)(*range(0, len(user_receiving_mail_choices)))
    user_receiving_mail = models.PositiveIntegerField(default=0, choices=get_field_choices(USER_RECEIVING_MAIL_TYPE))
    
    # this is used to tally up on whether we should deactivate the user's gcm device
    resend_counter = models.PositiveIntegerField(default=0)

    logs = models.TextField(null=True, blank=True)

    def terminate_active_tasks(self, user):

        if user.is_superuser or user.is_staff:
            # use command management - apps/api_messages/management/commands/terminate_active_tasks.py
            return management.call_command('terminate_active_tasks', 'Message', str(self.id), 'all')

        return "Not permitted to terminate running tasks"

    def __str__(self):
        return '{}. {}'.format(self.id, self.subject)


class MessageResend(CreatedModifiedMixin):
    '''
    Currently working for push notifications - tracking automated and scheduled messages that are resent
    '''

    # Owning object for the app model and instance using this file
    owning_object_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    owning_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, default=None)
    owning_object = GenericForeignKey('owning_content_type', 'owning_object_id')

    task_type = models.CharField(max_length=512, blank=True, null=True)

    resend_counter = models.PositiveIntegerField(default=0)
    resend_completed = models.BooleanField(default=False)

    logs = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return str('{}. {}'.format(self.owning_object_id, self.task_type))


class MessageCleanUp(CreatedModifiedMixin):

    # Owning object for the app model and instance using this file
    owning_object_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    owning_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, default=None)
    owning_object = GenericForeignKey('owning_content_type', 'owning_object_id')

    task_type = models.CharField(max_length=512)

    active = models.BooleanField(default=False)

    logs = models.TextField(default = "", blank=True, null=True)

    def __str__(self):
        return str('{}. {}'.format(self.owning_object_id, self.task_type))


class MessageTasks(CreatedModifiedMixin):

    # Owning object for the app model and instance using this file
    owning_object_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    owning_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, default=None)
    owning_object = GenericForeignKey('owning_content_type', 'owning_object_id')

    task_id = models.CharField(max_length=512, blank=True, null=True)

    task_type = models.CharField(max_length=512, blank=True, null=True)

    active = models.BooleanField(default=True)
    cancelled = models.BooleanField(default=False)

    logs = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return str('{}. {}'.format(self.owning_object_id, self.task_type))

    def terminate_active_tasks(self, user):

        if user.is_superuser or user.is_staff:
            try:
                # use command management - apps/marketing/management/commands/terminate_any_task.py
                management.call_command('terminate_any_task', str(self.task_id))
                self.active = False
                self.cancelled = True
                self.save()
                return "Done terminating running tasks for ID: {}".format(self.id)

            except Exception as e:
                return "Error terminating for ID: {} - {}".format(self.id, e)

        return "Not permitted to terminate running tasks"