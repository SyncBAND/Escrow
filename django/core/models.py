from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from versatileimagefield.fields import VersatileImageField, PPOIField

from .managers import UserManager

from apps.utils.models import CreatedModifiedMixin


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True, editable=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(_('active'), default=True)

    is_email_verified = models.BooleanField(default=False)
    is_cell_verified = models.BooleanField(default=False)

    avatar = VersatileImageField(
        'Image',
        upload_to='avatars/',
        ppoi_field='image_ppoi',
        null=True, blank=True
    )
    
    image_ppoi = PPOIField()
    group = models.CharField(_('group name'), max_length=128, blank=True)
    cell = models.CharField(max_length=17, validators=[RegexValidator(r'^\d{1,10}$')], blank=True, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def __str__(self):
        return self.email


class UserVerification(CreatedModifiedMixin):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    uid = models.TextField(null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    
    origin = models.TextField(null=True, blank=True)
    
    verified = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    email_address = models.EmailField(null=True, blank=True)
    
    message_sent = models.BooleanField(default=False)
    message_sent_details = models.TextField(null=True, blank=True)
    
    cancelled = models.BooleanField(default=False)
    cancelled_reason = models.TextField(null=True, blank=True)

    verification_type_choices = (
        (1, 'Cell'),
        (2, 'Email'),
    )
    verification_type = models.PositiveIntegerField(choices=verification_type_choices, default=2)

    def __str__(self):
        return self.user.first_name