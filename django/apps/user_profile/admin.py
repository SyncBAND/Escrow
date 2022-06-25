from django.contrib import admin

from .models import UserMode, UserProfile, UserSessions, UserChanges, UserVerifiedProfileCase

class UserModeAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = UserMode
admin.site.register(UserMode, UserModeAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = UserProfile
admin.site.register(UserProfile, UserProfileAdmin)

class UserSessionsAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = UserSessions
admin.site.register(UserSessions, UserSessionsAdmin)

class UserChangesAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = UserChanges
admin.site.register(UserChanges, UserChangesAdmin)

class UserVerifiedProfileCaseAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = UserVerifiedProfileCase
admin.site.register(UserVerifiedProfileCase, UserVerifiedProfileCaseAdmin)