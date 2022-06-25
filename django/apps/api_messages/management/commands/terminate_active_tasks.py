from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from apps.api_messages.models import MessageTasks

from nikanika.celery import app


class Command(BaseCommand):

    help = """
    Terminate active tasks for a app model (e.g. PushDevice) running on Celery usually when sending messages, e.g.
    >>> python manage.py terminate_active_tasks campaign_message_id task_type <<< 
    >>> python manage.py terminate_active_tasks all all -> this will terminate all active tasks running for all PushDevice's. task_type will be ignored  <<<
    >>> python manage.py terminate_active_tasks 156 all -> this will terminate all active tasks running for PushDevice with id=156 <<<
    >>> python manage.py terminate_active_tasks 201 execute -> this will terminate active tasks running for PushDevice with id=201 which were started using the "execute" function <<<
    """

    def add_arguments(self, parser):

        parser.add_argument('owning_content_type', type=str, help="Content type is needed e.g. PushDevice")
        parser.add_argument('owning_object_id', type=str, help="Object id is needed e.g. 5 or all")
        parser.add_argument('task_type', type=str,
                        help="Task type is need. Set task_type to either all, execute, clean_up_messages, resolve_sms_tasks, resolve_push_tasks or resend_for_push")

    def handle(self, *args, **kwargs):

        try:
            owning_content_type = ContentType.objects.get(model=kwargs['owning_content_type'].lower())
        except Exception as e:
            msg ='{} - Set owning_content_type to app model'.format(e)
            self.stdout.write(msg)
            return msg

        try:
            if kwargs['owning_object_id'] == 'all':
                pass
            elif not kwargs['owning_object_id'].isdigit():
                msg = 'Error: please enter a number for owning_object_id'
                self.stdout.write(msg)
                return msg
            owning_object_id = str(kwargs['owning_object_id'])
        except Exception as e:
            msg = 'Error: {}. Set to all or owning_object_id value'.format(e)
            self.stdout.write(msg)
            return msg

        try:
            task_type = str(kwargs['task_type'])
        except Exception as e:
            msg ='{} - Set task_type to either all, execute, clean_up_messages, resolve_sms_tasks, resolve_push_tasks or resend_for_push'.format(e)
            self.stdout.write(msg)
            return msg


        # check correct combination

        if owning_object_id.isdigit():
            if int(owning_object_id) < 1:
                msg = 'Error: please enter a number greater than 0 for owning_object_id or use the parameter, all'
                self.stdout.write(msg)
                return msg
            elif len(task_type) < 1:
                msg = 'Error: Set task_type value e.g. all, execute, clean_up_messages, resolve_sms_tasks, resolve_push_tasks or resend_for_push'
                self.stdout.write(msg)
                return msg


        try:

            if owning_object_id.isdigit():
                tasks = MessageTasks.objects.select_related().filter(
                    owning_content_type=owning_content_type, owning_object_id=owning_object_id, active=True)
            elif owning_object_id == "all":
                tasks = MessageTasks.objects.select_related().filter(owning_content_type=owning_content_type, active=True)
            else:
                msg = 'Error: please enter a number greater than 0 for owning_object_id or use the parameter, all'
                self.stdout.write(msg)
                return msg

            if task_type != "all":
                tasks = tasks.filter(task_type=task_type)

            count = 0
            for task in tasks:
                try:
                    app.control.revoke(task.task_id, terminate=True)
                    count += 1

                    task.cancelled = True
                    task.active = False
                    task.save()
                except:
                    pass


            msg = 'Done terminating: {} tasks'.format(count)
            self.stdout.write(msg)
            return msg

        except Exception as e:

            msg = 'Error: "%s".' % str(e)
            self.stdout.write(msg)
            return msg
