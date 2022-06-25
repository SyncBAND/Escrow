from rest_framework import serializers

from versatileimagefield.serializers import VersatileImageFieldSerializer

from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction

from .models import Chat, ChatList

from apps.support.models import Support
from apps.api_messages.models import Message
from apps.utils.notifications import email_notifier

from push_sdk.service import generic_send_push


class ChatListObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Support):
            return value
        raise Exception('Unexpected type of tagged object')


class ChatListSerializer(serializers.ModelSerializer):

    creator_name = serializers.SerializerMethodField()
    respondent_name = serializers.SerializerMethodField()

    creator_profile_pic = serializers.SerializerMethodField()
    respondent_profile_pic = serializers.SerializerMethodField()

    # content_object = ChatListObjectRelatedField(read_only=True)

    class Meta:
        model = ChatList
        fields = ('id', 'last_message', 'last_message_sent_by', 'creator', 'creator_name', 'respondent', 'respondent_name', 'creator_profile_pic', 'respondent_profile_pic', 'active_creator', 'active_respondent', 'creator_unread', 'respondent_unread', 'created', 'modified')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return

    def get_creator_name(self, obj):
        if obj:
            return obj.creator.first_name
        return ''
        
    def get_respondent_name(self, obj):
        if obj:
            return obj.respondent.first_name
        return ''

    def get_creator_profile_pic(self, obj):
        if obj:
            if obj.creator.avatar:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.creator.avatar.url)

        return 'https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-alt-512.png'

    def get_respondent_profile_pic(self, obj):
        if obj:
            if obj.respondent.avatar:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.respondent.avatar.url)
                
        return 'https://cdn1.iconfinder.com/data/icons/construction-tool-line-foreman-equipment/512/Wrench-512.png'


class ChatSerializer(serializers.ModelSerializer):

    creator_id = serializers.SerializerMethodField()

    creator_name = serializers.SerializerMethodField()
    respondent_name = serializers.SerializerMethodField()

    creator_profile_pic = serializers.SerializerMethodField()
    respondent_profile_pic = serializers.SerializerMethodField()
    
    image_1 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_2 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )

    class Meta:
        model = Chat
        fields = ('id', 'sent_by', 'chat_list', 'message', 'creator_name', 'creator_id', 'respondent_name', 'creator_profile_pic', 'respondent_profile_pic', 'image_1', 'image_2', 'active_creator', 'active_respondent', 'created')
        read_only_fields = ('id', 'sent_by')

    def create(self, validated_data):
        
        with transaction.atomic():

            user = self.context['request'].user

            validated_data['sent_by'] = user
            
            chat = Chat.objects.create(**validated_data)

            chat.chat_list.last_message = validated_data['message']
            chat.chat_list.last_message_sent_by = user.id
            chat.chat_list.save()

            subject = "{} messaged you".format(user.first_name)
            origin = "apps.chat.serializers.ChatSerializer.create"
        
            message = "{}: {}".format(user.first_name, validated_data['message'])

            # message for chatts
            email_message = str(validated_data['message']) + \
                '\n\nTime: ' + str(chat.created) + \
                '\n\nSee app for more'

            if chat.chat_list.creator == user:
                recipient = chat.chat_list.respondent
            else:
                recipient = chat.chat_list.creator

            # api_message = Message.objects.create(user=recipient, type=Message.MESSAGE_TYPE.PUSH_NOTIFICATION, subject=subject, message = message, recipients = recipient.email, origin=origin, status=Message.TYPE.MESSAGE_QUEUED_AT_NETWORK)

            # generic_send_push(recipient, api_message, data={'type': 'chat', 'chat_list_id': chat.chat_list.id, 'respondent': chat.chat_list.respondent.id, 'creator': chat.chat_list.creator.id}, resending=True, number_of_resends = 3, resend_interval_in_minutes = 2, _type="push_automated_resend", fall_back_to_sms=False, push_scheduled_resend=False)
            
            email_notifier.delay(recipient.id, origin=origin, message=email_message, subject=subject, email_to=[recipient.email])

            return chat

    def get_creator_name(self, obj):

        return obj.chat_list.creator.first_name

    def get_creator_id(self, obj):

        return obj.chat_list.creator.id

    def get_respondent_name(self, obj):

        return obj.chat_list.respondent.first_name

    def get_creator_profile_pic(self, obj):
        if obj.chat_list.creator.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.chat_list.creator.avatar.url)

        return 'https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-alt-512.png'

    def get_respondent_profile_pic(self, obj):
        if obj.chat_list.respondent.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.chat_list.respondent.avatar.url)
                
        return 'https://cdn1.iconfinder.com/data/icons/construction-tool-line-foreman-equipment/512/Wrench-512.png'