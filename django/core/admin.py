from django.contrib import admin
from .models import User, UserVerification
from django.contrib.auth.admin import UserAdmin
from django.forms import Textarea


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'cell', 'first_name', 'last_name', 'group')
    list_filter = ('email', 'cell', 'first_name', 'last_name', 'group', 'is_staff',
                   'is_active')
    ordering = ('-date_joined',)
    list_display = ('email', 'cell', 'first_name', 'last_name', 'group', 'is_staff',
                    'is_active', 'avatar')
    fieldsets = (
        (None, {'fields': ('email', 'cell', 'first_name', 'last_name', 'password', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
        ('Owner', {'fields': ('group',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'cell', 'first_name', 'last_name', 'password1', 'password2', 'avatar')
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
        ('Owner', {'fields': ('group',)}),
    )


admin.site.register(User, UserAdminConfig)

class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ["__str__", "message_sent", "message_sent_details", "verified", "expired"]
    class Meta:
        model = UserVerification

admin.site.register(UserVerification, UserVerificationAdmin)
