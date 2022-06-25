from django.db import models
from django.utils import timezone


class CreatedModifiedMixin(models.Model):

    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()

        self.modified = timezone.now()
        super(CreatedModifiedMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class PermissionsMixin(models.Model):
    """
    Django abstract class mixin for access permissions defined on models.
    """
    #:author: Kabelo Twala

    @classmethod
    def has_permission(cls, request):
        return False

    def has_object_permission(self, request):
        return False

    class Meta:
        abstract = True
