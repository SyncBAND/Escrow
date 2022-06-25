from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Q, Value
from django.db.models.functions import Concat

from .models import PushDevice
from apps.api_messages.models import Message, MessageTasks

from datetime import datetime, timedelta

from decouple import config

# will be copied into it's rightful sdk
def send_push(device, api_message, data, message_resent=False, fall_back_to_sms=False,
              push_automated_resend=False, push_scheduled_resend=False):

    message = api_message.message

    # for log purposes - might be overly done but.. hay `\(..)/`
    extra_response = ""
    if message_resent:
        extra_response = "push resent"
    if fall_back_to_sms:
        extra_response = "{} > send sms if push fails".format(extra_response)
    if push_automated_resend:
        extra_response = "{} > push_automated_resend".format(extra_response)
    if push_scheduled_resend:
        extra_response = "{} > push_scheduled_resend".format(extra_response)

    try:

        # when sending scheduled push - make sure push hasn't been sent or is sent to network
        final_check = Message.objects.select_related().filter(type=Message.MESSAGE_TYPE.PUSH_NOTIFICATION, user=api_message.user)

        if push_automated_resend:
            # when sending scheduled push - check if push hasn't been sent or is sent to network
            final_check = final_check.filter(Q(status=Message.TYPE.MESSAGE_QUEUED_AT_NETWORK) |
                                             Q(status=Message.TYPE.MESSAGE_SENT_TO_NETWORK))

        elif push_scheduled_resend:
            # when sending scheduled push - check if push is sent to network
            final_check = final_check.filter(status=Message.TYPE.MESSAGE_SENT_TO_NETWORK)

        else:
            # when sending/resending - check if push hasn't been sent
            final_check = final_check.filter(status=Message.TYPE.MESSAGE_QUEUED_AT_NETWORK)

        final_check = final_check.filter(id=api_message.id)


        if final_check.exists():
            try:
                push_response = device.send_message(message=message, api_key=config('FCM_API_KEY'), api_message_id=api_message.id, data=data)

            except Exception as e:
                # handle error
                return update_api_message(api_message, str(e), "Message: {} - Push Error: {}".format(api_message.id, str(e)), Message.TYPE.MESSAGE_UNDELIVERED, fall_back_to_sms=fall_back_to_sms,
                                          extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)


            if push_response is not None:
                if 'results' in push_response[0]:

                    response = push_response[0]['results'][0]

                    if 'message_id' in response:

                        # check for number of scheduled resends
                        # if resend_counter >= 20, deactivate device
                        #     this helps jobbers receive sms sooner if push & sms are chosen
                        if push_automated_resend or push_scheduled_resend:
                            api_message.resend_counter = api_message.resend_counter + 1
                            device.resend_counter = device.resend_counter + 1
                            device.save()

                        if api_message.remote_id:
                            api_message.remote_id = "{}, {}".format(api_message.remote_id, response['message_id'])
                        else:
                            api_message.remote_id = response['message_id']

                        # what are the odds that by the time this function updates the database - the api_message call from the app
                        # has already updated the db with the delivered status and this overrides the status??
                        # might be reasonable to delay the api call from the app - for now will test theory using additional table

                        if push_scheduled_resend:
                            # difference is value for fall_back_to_sms. if true, check if message is defaulted to sms
                            update_api_message(api_message, response, response,
                                           Message.TYPE.MESSAGE_SENT_TO_NETWORK,
                                           fall_back_to_sms=fall_back_to_sms, extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)
                        else:
                            update_api_message(api_message, response, response,
                                           Message.TYPE.MESSAGE_SENT_TO_NETWORK,
                                           fall_back_to_sms=fall_back_to_sms, extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)

                    elif 'error' in response:

                        if "HTTPSConnectionPool(host='fcm.googleapis.com', port=443)" not in response[
                            'error'] or "HTTPSConnectionPool(host=\'fcm.googleapis.com\', p   ort=443)" not in \
                                response['error']:
                            update_api_message(api_message, response, "Device: {} - Push Error: ".format(device.id, response),
                                        Message.TYPE.MESSAGE_UNDELIVERED, fall_back_to_sms=fall_back_to_sms,
                                        extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)

                    else:
                        update_api_message(api_message, response, "Device: {} - Push Error: ".format(device.id, response), Message.TYPE.MESSAGE_UNDELIVERED,
                                    fall_back_to_sms=fall_back_to_sms, extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)

                else:
                    update_api_message(api_message, "Failed at network", "Device: {} - Push Error: Failed at network: {}".format(device.id, Message.TYPE.MESSAGE_FAILED_AT_NETWORK),
                                       Message.TYPE.MESSAGE_UNDELIVERED, fall_back_to_sms=fall_back_to_sms,
                                       extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)

            else:
                update_api_message(api_message, "Returned Null", 'Message: {} - Push Error: Send response returned null'.format(api_message.id), Message.TYPE.MESSAGE_UNDELIVERED,
                                   fall_back_to_sms=fall_back_to_sms, extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)

        else:
            if fall_back_to_sms:
                update_api_message(api_message, "Not queued", "Message: {} - Push Error: Message not MESSAGE_QUEUED_AT_NETWORK".format(api_message.id), Message.TYPE.MESSAGE_UNDELIVERED,
                               fall_back_to_sms=fall_back_to_sms, extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)
            else:
                # update all
                # final_check.update(
                #     status=Message.TYPE.MESSAGE_UNDELIVERED,
                #     logs=Concat('logs', Value(
                #         '\n\n{} Message error ID: {}. Message not MESSAGE_QUEUED_AT_NETWORK'.format(timezone.localtime(timezone.now()), api_message.id)))
                # )
                pass

    except Exception as e:
        update_api_message(api_message, 'No response', "Message: {} - Push Error: {}".format(api_message.id, e), Message.TYPE.MESSAGE_UNDELIVERED,
                           fall_back_to_sms=fall_back_to_sms, extra_response=extra_response, push_scheduled_resend=push_scheduled_resend)


def update_api_message(api_message, response, logs, remote_message_status, fall_back_to_sms=False, extra_response="", push_scheduled_resend=False):

    '''SETTING REMOTE_MESSAGE_STATUS CONFIG BELOW'''

    api_message.remote_message_status = remote_message_status

    if api_message.logs is None:
        api_message.logs = "{} {} - {} - {}".format(timezone.localtime(timezone.now()), logs, response, extra_response)
    else:
        api_message.logs = "{}\n\n{} {} - {} - {}".format(api_message.logs, timezone.localtime(timezone.now()) , logs, response, extra_response)

    if fall_back_to_sms and remote_message_status!=Message.TYPE.MESSAGE_SENT_TO_NETWORK:
        #handle sms
        api_message.save()
    else:
        # before updating
        api_message.status = remote_message_status
        api_message.save()

# for reuse across the platform
def generic_send_push(user, api_message, data={}, resending=False, number_of_resends = 3, resend_interval_in_minutes = 2, _type="", fall_back_to_sms=False, push_scheduled_resend=False):
    from .tasks import generic_resend_for_push

    '''
    for reuse across the platform - tracks push with automated resends and defaults to sms if push fails

    :param user: user object - required
    :param api_message: Message object - required
    :param number_of_resends: Resend interval in minutes
    :param resend_interval_in_minutes: Resend interval in minutes
    :param _type: string between push_automated_resend and push_scheduled_resend
    :param fall_back_to_sms: boolean - send sms if push fails
    :return:
    '''

    try:
        
        user_push_device = PushDevice.objects.select_related().filter(
            user_id=user.id,
            active=True
        )

        if user_push_device.count() > 0:

            owning_content_type = ContentType.objects.get_for_model(Message)
            owning_object_id = api_message.id

            if _type == "push_automated_resend":
                # send message
                for device in user_push_device:

                    send_push(device, api_message, data, fall_back_to_sms=fall_back_to_sms, push_automated_resend=True)

                if resending:
                    task = generic_resend_for_push.apply_async(
                        args=[user.id, api_message.id, data, number_of_resends, resend_interval_in_minutes, "push_automated_resend", fall_back_to_sms],
                        eta=timezone.localtime(timezone.now()) + timedelta(minutes=2))

                    MessageTasks.objects.create(owning_content_type=owning_content_type,
                                                owning_object_id=owning_object_id,
                                                task_type="push_automated_resend", task_id=task.id)

            elif _type == "push_scheduled_resend":
                # send message
                for device in user_push_device:

                    send_push(device, api_message, data, fall_back_to_sms=fall_back_to_sms, push_scheduled_resend=True)


                if resending:
                    task = generic_resend_for_push.apply_async(
                        args=[user.id, api_message.id, data, number_of_resends, resend_interval_in_minutes, "push_scheduled_resend", fall_back_to_sms],
                        eta=timezone.localtime(timezone.now()) + timedelta(minutes=2))

                    MessageTasks.objects.create(owning_content_type=owning_content_type,
                                                owning_object_id=owning_object_id,
                                                task_type="push_scheduled_resend", task_id=task.id)

            else:
                # send message | caters well for resending push notifications outside the marketing campaign
                for device in user_push_device:
                    send_push(device, api_message, data, fall_back_to_sms=fall_back_to_sms, push_scheduled_resend=push_scheduled_resend)

            return {'success': True, 'detail': 'No errors'}

        else:

            api_message.status = Message.TYPE.MESSAGE_DOES_NOT_EXIST
            api_message.status_response = 'Device does not exist'
            api_message.logs = "{}\n\n{} Device does not exist".format(api_message.logs, timezone.localtime(timezone.now()))
            api_message.save()
        
            return {'success': False, 'detail': 'No device'}

    except Exception as e:
        print(e)
        return {'success': False, 'detail': str(e)}