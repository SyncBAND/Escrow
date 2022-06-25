from django.db import models
from django.conf import settings
from collections import namedtuple

from apps.utils.models import CreatedModifiedMixin

from apps.utils.views import get_field_choices

from versatileimagefield.fields import VersatileImageField, PPOIField

# https://stackoverflow.com/questions/20895429/how-exactly-do-django-content-types-work
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# initiated by respondant
class ChatList(CreatedModifiedMixin):

    # because of chats from different apps - e.g support, enquiries
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    # object creator
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='creator')
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='respondent')
    
    creator_unread = models.IntegerField(default=0)
    respondent_unread = models.IntegerField(default=0)

    active_creator = models.BooleanField(default=True)
    active_respondent = models.BooleanField(default=True)

    last_message = models.TextField(null=True, blank=True)
    last_message_sent_by = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return "{} {}: {}, {}".format(self.object_id, self.content_type, self.creator.first_name, self.respondent.first_name)


class Chat(CreatedModifiedMixin):

    chat_list = models.ForeignKey(ChatList, on_delete=models.CASCADE, null=True, blank=True)

    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_by')
    
    message = models.TextField(null=True, blank=True)

    image_1 = VersatileImageField(
        'Image',
        upload_to='communication/',
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to='communication/',
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to='communication/',
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to='communication/',
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    active_creator = models.BooleanField(default=True)
    active_respondent = models.BooleanField(default=True)

    def __str__(self):
        if self.chat_list:
            return "{}. {}, {}".format(self.id, self.chat_list.creator.first_name, self.chat_list.respondent.first_name)
        return str(self.id)


