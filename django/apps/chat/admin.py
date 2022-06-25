from django.contrib import admin

from .models import Chat, ChatList

class ChatAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Chat

admin.site.register(Chat, ChatAdmin)

class ChatListAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = ChatList

admin.site.register(ChatList, ChatListAdmin)
