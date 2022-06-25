from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from collections import namedtuple

from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices


# "FCM" = "Firebase Cloud Message"
class PushDevice(CreatedModifiedMixin):

	name = models.CharField(max_length=255, verbose_name=_("Name"), blank=True, null=True)
	active = models.BooleanField(
		verbose_name=_("Is active"), default=True,
		help_text=_("Inactive devices will not be sent notifications")
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
	)

	app_version = models.CharField(max_length=128, blank=True, null=True)
	resend_counter = models.PositiveIntegerField(default=0, blank=True, null=True)
    
	device_id = models.CharField(max_length=255,
		verbose_name=_("Push Device ID"), blank=True, null=True, db_index=True,
	)

	registration_id = models.TextField(verbose_name=_("Registration ID"))

	PLATFORM_DICT = {
		'ANDROID': 0,
		'IOS': 1,
	}

	_platform = (
		'ANDROID',
		'IOS',
	)
	TYPE = namedtuple('TYPE', _platform)(*range(0, len(_platform)))

	platform = models.PositiveIntegerField(
		default=TYPE.ANDROID,
		choices=get_field_choices(TYPE),
	)

	class Meta:
		verbose_name = _("FCM device")

	def __str__(self):
		return (
			self.name or str(self.device_id) or
			"%s for %s" % (self.__class__.__name__, self.user or "unknown user")
		)
        
	def send_message(self, message='', api_key='', api_message_id=0, data={}, **kwargs):
		from .action import send_message as fcm_send_message

		all_data = kwargs.pop("extra", {})
		if message is not None:
			all_data["message"] = message
		
		all_data.update(data)

		return fcm_send_message(
			self.registration_id, all_data, api_key=api_key, app_version=self.app_version, api_message_id=api_message_id, platform=self.platform, **kwargs
		)

	def activate(self, user):
		if not self.active:
			self.active = True
			self.save()
		return

	def deactivate(self, user):
		if self.active:
			self.active = False
			self.save()
		return