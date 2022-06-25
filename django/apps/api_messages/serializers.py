from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):

    m_type = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    user_receiving_mail_choice = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'user', 'subject', 'message', 'recipients', 'origin', 'remote_id', 'remote_message_status', 'resend_counter', 'logs', 'status', 'current_status', 'type', 'm_type', 'user_receiving_mail', 'user_receiving_mail_choice')
    
    def create(self, validate_data):

        user = self.context['request'].user
        
        return Message.objects.create(**validate_data)
    
    def update(self, instance, validated_data):
        return 

    def get_m_type(self, obj):

        return Message._type[obj.type]
    
    def get_current_status(self, obj):

        return Message.status_choices[obj.status]
    
    def get_user_receiving_mail_choice(self, obj):

        return Message.user_receiving_mail_choices[obj.user_receiving_mail]