from django.core.management.base import BaseCommand
from django.db.models import Q
from django.conf import settings

from apps.api_messages.models import Message

# from constance import config

class Command(BaseCommand):
    # python manage.py resolve_api_message_responses
    
    help = 'Resolve unhandled remote_message_status that had a successful response. e.g. >>> python manage.py resolve_api_message_responses'

    def handle(self, *args, **kwargs):

        try:
            
            search_text = '"status":1,"message":"Sent"'
            messages = Message.objects.filter( Q(response__contains=search_text), status = int(Message.CONSTANCE['MESSAGE_UNDELIVERED']) )
            count = 0
            for message in messages:
                count = count + 1
                message.remote_message_status = 1
                message.status = 1
                message.save()

            self.stdout.write('Done: "%s".' % str(count) )
        except Exception as e:

            self.stdout.write('Error: "%s".' % str(e) )

    