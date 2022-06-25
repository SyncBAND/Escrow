from django.conf import settings
from django.db import models

from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator
from apps.user_profile.models import UserProfile

from versatileimagefield.fields import VersatileImageField, PPOIField

from collections import namedtuple

from django.contrib.contenttypes.fields import GenericRelation


class Support(CreatedModifiedMixin):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_creator")

    title = models.CharField(max_length=128, null=False)
    description = models.TextField(null=True, blank=True)
    problem = models.CharField(max_length=128, null=True, blank=True)

    status_choices = (
        'Processing',
        'Cancelled',
        'Attended',
        'Deleted',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))
    status_details = models.TextField(null=True, blank=True)

    reference = models.CharField(max_length=32, null=False)

    image_1 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    image_5 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_5',
        null=True, blank=True
    )
    image_ppoi_5 = PPOIField()

    image_6 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_6',
        null=True, blank=True
    )
    image_ppoi_6 = PPOIField()

    image_7 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_7',
        null=True, blank=True
    )
    image_ppoi_7 = PPOIField()

    image_8 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_8',
        null=True, blank=True
    )
    image_ppoi_8 = PPOIField()

    city = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    province = models.CharField(max_length=128, null=True, blank=True)

    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)
    
    chat = GenericRelation('chat.ChatList')

    # -------- 

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                reference = random_generator(length=9, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(reference=reference).only('reference').exists():
                    break
            self.reference = reference
        return super(Support, self).save(*args, **kwargs)
        
    def __str__(self):
        return str(self.id)


class SupportActivity(CreatedModifiedMixin):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_activity_creator")
    
    support = models.ForeignKey(Support, on_delete=models.CASCADE)

    _status_choices = {
        'Processing': 0,
        'Cancelled': 1,
        'Attended': 2,
        'Deleted': 3,
    }

    previous_status_choices = (
        'Processing',
        'Cancelled',
        'Attended',
        'Deleted',
    )
    PREVIOUS_STATUS = namedtuple('PREVIOUS_STATUS', previous_status_choices)(*range(0, len(previous_status_choices)))
    previous_status = models.PositiveIntegerField(default=0, choices=get_field_choices(PREVIOUS_STATUS))

    previous_status_details = models.TextField(null=True, blank=True)

    status_choices = (
        'Processing',
        'Cancelled',
        'Attended',
        'Deleted',
    )
    STATUS = namedtuple('STATUS', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS))

    status_details = models.TextField(null=True, blank=True)

    image_1 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    image_5 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_5',
        null=True, blank=True
    )
    image_ppoi_5 = PPOIField()

    image_6 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_6',
        null=True, blank=True
    )
    image_ppoi_6 = PPOIField()

    image_7 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_7',
        null=True, blank=True
    )
    image_ppoi_7 = PPOIField()

    image_8 = VersatileImageField(
        'Image',
        upload_to="support/",
        ppoi_field='image_ppoi_8',
        null=True, blank=True
    )
    image_ppoi_8 = PPOIField()

    city = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    province = models.CharField(max_length=128, null=True, blank=True)

    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)


    def __str__(self):
        return "{}: {} -> {}".format(str(self.support.title), str(SupportActivity.STATUS[self.status]), str(SupportActivity.STATUS[self.previous_status]))


class SupportRatings(CreatedModifiedMixin):

    user_profile_making_rating = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    support_being_rated = models.ForeignKey(Support, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField(default=0)
    review = models.TextField(null=True, blank=True)

    editted = models.BooleanField(default=False)

    def __str__(self):
        return "{} rated {}: ".format(str(self.user_profile_making_rating.user.first_name), str(self.support_being_rated.title))


class SupportRatingsHistory(CreatedModifiedMixin):

    support_ratings = models.ForeignKey(SupportRatings, on_delete=models.CASCADE)

    previous_rating = models.PositiveIntegerField(default=0)
    previous_review = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} changed rating on {}: ".format(str(self.support_ratings.user_profile_making_rating.user.first_name), str(self.support_ratings.support_being_rated.title))
