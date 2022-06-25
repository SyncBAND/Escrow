from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from django.utils import timezone

from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.db.models import Q, Value, F
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.conf import settings

from apps.api_messages.models import Message, MessageCleanUp, MessageResend, MessageTasks
from .service import generic_send_push

from .models import PushDevice

logger = get_task_logger(__name__)


@shared_task(name="resolve_push_tasks", time_limit=7200, soft_time_limit=7200, max_retries=5)
def resolve_push_tasks(message_campaign):

    logger.info("Push log: Updating push active devices...")

    owning_content_type = ContentType.objects.get_for_model(PushDevice)
    owning_object_id = message_campaign.id

    MessageTasks.objects.filter(active=True, task_type='resolve_push_tasks',
                owning_content_type=owning_content_type, owning_object_id=owning_object_id).update(active=False)

    try:

        try:

            devices = PushDevice.objects.select_related().filter(resend_counter__gte=20)
            count = 0

            for device in devices:
                count = count + 1
                device.active = False
                device.save()

            logger.info("Push log: Deactivated " + str(count) + " devices...")

            MessageCleanUp.objects.filter(owning_content_type=owning_content_type, owning_object_id=owning_object_id,
                task_type="resolve_push_tasks").update( active=False,
                logs=Concat('logs', Value('\n\n{} - Push log: Deactivated: {}'.format(timezone.localtime(timezone.now()), count)))
            )

        except Exception as e:

            logger.info("Push log: Error " + str(e))

            MessageCleanUp.objects.filter(owning_content_type=owning_content_type, owning_object_id=owning_object_id,
                task_type="resolve_push_tasks").update( active=False,
                logs=Concat('logs', Value('\n\n{} - Push log: Error: {}'.format(timezone.localtime(timezone.now()), e)))
            )

    except SoftTimeLimitExceeded:

        logger.exception("Push update log error - retrying in 30 seconds")

        MessageCleanUp.objects.filter(owning_content_type=owning_content_type, owning_object_id=owning_object_id,
            task_type="resolve_push_tasks").update( active=False,
            logs=Concat('logs', Value('\n\n{} - Push update log error: SoftTimeLimitExceeded'.format(timezone.localtime(timezone.now()))))
        )

        resolve_push_tasks.retry(countdown=30)

    except Exception as e:

        logger.exception("Push update log error: " + str(e) + " - retrying in 60 seconds")

        MessageCleanUp.objects.filter(owning_content_type=owning_content_type, owning_object_id=owning_object_id,
            task_type="resolve_push_tasks").update( active=False,
            logs=Concat('logs', Value('\n\n{} - Push log: Error: {}'.format(timezone.localtime(timezone.now()), e)))
        )

    return


@shared_task(name="generic_resend_for_push", time_limit=7200, soft_time_limit=7200, max_retries=5, task_track_started=True)
def generic_resend_for_push(user_id, api_message_id, data={}, number_of_resends=3, resend_interval_in_minutes = 2, _type="push_automated_resend", fall_back_to_sms=False, resend_count=0):

    try:
        user = get_user_model().objects.get(id=user_id)

        # get a fresh version
        api_message = Message.objects.select_related().get(id=api_message_id)
    except Exception as e:
        print(e)
        return
        
    try:

        owning_content_type = ContentType.objects.get_for_model(Message)
        owning_object_id = api_message_id

        if _type == "push_automated_resend":
            number_of_resend_times = 3
            interval_in_minutes = 2

        else:
            number_of_resend_times = number_of_resends
            interval_in_minutes = resend_interval_in_minutes

        MessageTasks.objects.filter(active=True, task_type='push_automated_resend',
                                    owning_content_type=owning_content_type,
                                    owning_object_id=owning_object_id).update(active=False)

        MessageTasks.objects.filter(active=True, task_type='push_scheduled_resend',
                                    owning_content_type=owning_content_type,
                                    owning_object_id=owning_object_id).update(active=False)

        if resend_count < number_of_resend_times:

            # if condition fail - no need to resend anything
            if api_message.status == Message.TYPE.MESSAGE_QUEUED_AT_NETWORK or api_message.status == Message.TYPE.MESSAGE_SENT_TO_NETWORK:

                resend_count = resend_count + 1

                try:

                    # after resending scheduled, check if sms was also selected as channel, if yes - send sms
                    if number_of_resend_times == resend_count and fall_back_to_sms and _type == "push_scheduled_resend":
                        generic_send_push(user, api_message, data=data, fall_back_to_sms=False, push_scheduled_resend=False)
                    else:
                        generic_send_push(user, api_message, data=data)

                except Exception as e:
                    api_message.logs = "{}\n\n{} Error: generic_resend_for_push - {}".format(api_message.logs,
                                                                                                 timezone.localtime(timezone.now()), e)
                    api_message.status = Message.TYPE.MESSAGE_UNDELIVERED
                    api_message.save()

                task = generic_resend_for_push.apply_async(args=[user.id, api_message_id, data, number_of_resends, resend_interval_in_minutes, _type, fall_back_to_sms, resend_count],
                                                   eta=timezone.localtime(timezone.now()) + timedelta(minutes=interval_in_minutes))

                MessageTasks.objects.create(owning_content_type=owning_content_type,
                                            owning_object_id=owning_object_id, task_type=_type, task_id=task.id)


                try:
                    resend = MessageResend.objects.select_related().get(owning_content_type=owning_content_type,
                                                                        owning_object_id=owning_object_id,
                                                                        task_type=_type)
                    resend.logs = '{}\n\n{} - Resending {} generic_send_push'.format(resend.logs, timezone.localtime(timezone.now()), resend_count)
                    resend.resend_counter = resend.resend_counter + 1
                    if _type == "push_automated_resend" and number_of_resend_times == resend_count:
                        resend.resend_completed = True
                    resend.save()
                except:
                    MessageResend.objects.create(owning_content_type=owning_content_type,
                                                 owning_object_id=owning_object_id, task_type=_type, resend_counter=1,
                                                 logs='{} - Resending {} generic_send_push'.format(
                                                     timezone.localtime(timezone.now()), resend_count))

                return

        elif _type == "push_automated_resend":  # this makes sure the scheduled resending runs once

            task = generic_resend_for_push.apply_async(args=[user.id, api_message_id, data, number_of_resends, resend_interval_in_minutes, "push_scheduled_resend", fall_back_to_sms, 0],
                                               eta=timezone.localtime(timezone.now()) + timedelta(minutes=resend_interval_in_minutes))

            MessageTasks.objects.create(owning_content_type=owning_content_type,
                                        owning_object_id=owning_object_id, task_type=_type, task_id=task.id)

            return


        MessageResend.objects.filter(owning_content_type=owning_content_type, owning_object_id=owning_object_id,
            task_type=_type).update(resend_completed = True,
            logs=Concat('logs', Value('\n\n{} - Done: {} for generic_resend_for_push'.format(timezone.localtime(timezone.now()), _type)))
        )

        try:
            api_message.logs = '{}\n\n{} - Done: {} for generic_resend_for_push'.format(api_message.logs, timezone.localtime(timezone.now()), _type)
            api_message.save()
        except Exception as e:
            print(e)
            pass


    except SoftTimeLimitExceeded:
        msg_ = "SoftTimeLimitExceeded - retrying in 30 seconds"

        logger.exception(msg_)

        try:
            api_message.logs = '{}\n\n{} - Error: {} for generic_resend_for_push - {}'.format(api_message.logs, timezone.localtime(timezone.now()), _type, msg_)
            api_message.save()
        except Exception as e:
            pass

        generic_resend_for_push.retry(countdown=30)

    except Exception as e:
        msg_ = "Exception Error: {}".format(e)

        logger.exception(msg_)

        try:
            api_message.logs = '{}\n\n{} - Exception Error: {} for generic_resend_for_push - {}'.format(api_message.logs, timezone.localtime(timezone.now()), _type, msg_)
            api_message.save()
        except Exception as e:
            pass