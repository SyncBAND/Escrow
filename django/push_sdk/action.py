from .models import PushDevice
from apps.api_messages.models import Message

import json
import requests

def send_message(registration_ids, data, api_key=None, api_message_id=0, app_version=None, platform=PushDevice.TYPE.ANDROID, **kwargs):

    try:
        api_message = Message.objects.get(id=api_message_id)
    except:
        api_message_id = 0
        api_message_url = ''

    data['url'] = ''
    data['message_id'] = api_message_id

    payload = {
        "to": registration_ids,
        "data": data
    }

    payload["android"] = {
        "ttl": "0s",
        "notification": {
            "click_action": "OPEN_ACTIVITY_1"
        },
        "priority": "high"
    }

    payload["content_available"] = True
    payload["apns"] = {
        "headers": {
            "apns-priority": 10,
        },
        "payload": {
            "aps": {
                "category": "NEW_MESSAGE_CATEGORY"
            }
        }
    }

    if platform == PushDevice.TYPE.IOS:
        payload["notification"] = {
            "body": data["message"]
        }
    
    json_payload = json.dumps(payload).encode("utf-8")

    response = send(
        json_payload, "application/json", api_key=api_key
    )

    if type(response) == requests.exceptions.ConnectionError:
        return [{
            'results': [{ "error": str(response) }],
        }]
    elif type(response) == requests.models.Response:
        if response.status_code == 200:
            response = response.json()
        else:
            return [{
                'results': [{"error": str(response.status_code) + ': ' +response.reason}],
            }]
    else:
        return [{
            'results': [{"error": str(response) }],
        }]
    
    return handle_response(registration_ids, response, api_key)


def send(data, content_type, api_key):

    FCM_POST_URL = "https://fcm.googleapis.com/fcm/send"
            
    headers = {
        "Content-Type": content_type,
        "Authorization": "key=%s" % (api_key),
        "Content-Length": str(len(data)),
    }

    try:
        response =  requests.post(FCM_POST_URL, data=data, headers=headers, timeout=5)
    except Exception as e:
        response = e

    return response
    
def handle_response(registration_ids, response_data, api_key=None):

    response = response_data

    if response.get("failure") or response.get("canonical_ids"):
        ids_to_remove, old_new_ids = [], []
        throw_error = False

        for index, result in enumerate(response["results"]):
            error = result.get("error")
            if error:
                # https://firebase.google.com/docs/cloud-messaging/http-server-ref#error-codes
                # If error is NotRegistered or InvalidRegistration, then we will deactivate devices
                # because this registration ID is no more valid and can't be used to send messages,
                # otherwise raise error
                if error in ("NotRegistered", "InvalidRegistration"):
                    ids_to_remove.append(registration_ids[index])
                # else:
                #     throw_error = True

            # If registration_id is set, replace the original ID with the new value (canonical ID)
            # in your server database. Note that the original ID is not part of the result, you need
            # to obtain it from the list of registration_ids in the request (using the same index).
            new_id = result.get("registration_id")
            if new_id:
                old_new_ids.append((registration_ids[index], new_id))

        if ids_to_remove:
            removed = PushDevice.objects.filter(
                registration_id__in=ids_to_remove
            ).update(active=False)

        for old_id, new_id in old_new_ids:
            handle_canonical_id(new_id, old_id)

    return [response]

def handle_canonical_id(canonical_id, current_id):
    """
    Handle situation when FCM server response contains canonical ID
    """
    if GCMDevice.objects.filter(registration_id=canonical_id, active=True).exists():
        GCMDevice.objects.filter(registration_id=current_id).update(active=False)
    else:
        GCMDevice.objects.filter(registration_id=current_id).update(registration_id=canonical_id)