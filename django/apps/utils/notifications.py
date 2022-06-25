from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone

from core.models import UserVerification

from apps.api_messages.models import Message
from apps.user_profile.models import UserProfile
from .tokens import email_verification_token

from celery import shared_task


@shared_task(name="mail_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def mail_notifier(user_id, domain, origin='', verification_type=2, subject='', sign_off='', email_to='', cancelled=False, cancelled_reason=""):

    # reason we pass user_id instead of user object
    # kombu.exceptions.EncodeError: Object of type User is not JSON serializable
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return

    try:

        try:
            verifier = UserVerification.objects.get(user=user, verified=False, expired=False, verification_type=verification_type, cancelled=False)
            uid = verifier.uid
            token = verifier.token
            verifier.email_address=email_to
        except UserVerification.DoesNotExist:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            UserVerification.objects.filter(user=user, verified=False, expired=False, verification_type=verification_type, cancelled=False).update(expired=True, cancelled=cancelled, cancelled_reason="Creating new notification: " + str(cancelled_reason))
            verifier = UserVerification.objects.create(user=user, uid=uid, token=token, origin=origin, verified=False, expired=False, verification_type=verification_type, email_address=email_to)
            UserProfile.objects.filter(user_id=user_id).update(email=email_to)
        except Exception as e:
            verifier = UserVerification.objects.filter(user=user, verified=False, expired=False, verification_type=verification_type, cancelled=False).first()
        
        message = render_to_string('verify_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
            'sign_off': sign_off
        })

        try:
            email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [email_to])
            response = email.send()
            verifier.message_sent = True
            verifier.save()

            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin)
                existing.status = Message.TYPE.MESSAGE_DELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(response))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(response))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response))

        except Exception as e:
            verifier.message_sent = False
            verifier.message_sent_details = "{}\n\n{} - {}".format(verifier.message_sent_details, timezone.localtime(timezone.now()) , str(e))
            verifier.save()
            
            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin)
                existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))

    except Exception as e:
        print(e)

        try:
            existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin)
            existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
            existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
            existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
            existing.save()
        except:
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = '', recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))


@shared_task(name="email_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def email_notifier(user_id, origin='', subject='', message='', email_to=[]):
    
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return

    try:
        try:
            email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, email_to)
            response = email.send()

            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin)
                existing.status = Message.TYPE.MESSAGE_DELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(response))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(response))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response))
                
        except Exception as e:

            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin)
                existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))
        
    except Exception as e:
        print(e)
        try:
            existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin)
            existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
            existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
            existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
            existing.save()
        except:
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))


@shared_task(name="email_update_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def email_update_notifier(user_id, subject='', msg='', origin='', sign_off='', email_to='', user_receiving_mail=0):
    
    # reason we pass user_id instead of user object
    # kombu.exceptions.EncodeError: Object of type User is not JSON serializable
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return
        
    try:

        message = "Hi " + user.first_name + ", \n\n" + str(msg) + "\n\n" + "Regards,\n\n"+ sign_off

        try:
            email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [email_to])
            response = email.send()
            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, user_receiving_mail=user_receiving_mail)
                existing.status = Message.TYPE.MESSAGE_DELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(response))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(response))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response), user_receiving_mail=user_receiving_mail)
                
        except Exception as e:
            print(e)

            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, user_receiving_mail=user_receiving_mail)
                existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e), user_receiving_mail=user_receiving_mail)

    except Exception as e:
        print(e)
        try:
            existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = msg, recipients = email_to, origin=origin, user_receiving_mail=user_receiving_mail)
            existing.status = Message.TYPE.MESSAGE_UNDELIVERED
            existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
            existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
            existing.save()
        except:
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = msg, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e), user_receiving_mail=user_receiving_mail)


@shared_task(name="transaction_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def transaction_notifier(user_id, origin='', subject='', message='', email_to=[], user_receiving_mail=0):
    
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return

    try:
        try:
            message_greeting = 'Hi,'
            if user.first_name:
                message_greeting = 'Hi ' + user.first_name + ','

            message_footer = 'Kind Regards,\n\nThe Team'

            response = client_email_notification(subject=subject, message_greeting=message_greeting, message_body=message, message_footer=message_footer, email_from=settings.EMAIL_HOST_USER, email_from_name='Nika Nika', email_to=email_to)

            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, user_receiving_mail=user_receiving_mail)
                existing.status = Message.TYPE.MESSAGE_DELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(response))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(response))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response), user_receiving_mail=user_receiving_mail)

        except Exception as e:
            print('In e')
            print(e)
            try:
                existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, user_receiving_mail=user_receiving_mail)
                existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
                existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
                existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
                existing.save()
            except:
                Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e), user_receiving_mail=user_receiving_mail)
        
    except Exception as e:
        print('Out e')
        print(e)
        try:
            existing = Message.objects.get(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, user_receiving_mail=user_receiving_mail)
            existing.status = Message.TYPE.MESSAGE_UNDELIVERED 
            existing.remote_message_status = "{}\n\n{}".format(existing.remote_message_status, str(e))
            existing.status_response = "{}\n\n{}".format(existing.status_response, str(e))
            existing.save()
        except:
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e), user_receiving_mail=user_receiving_mail)


def client_email_notification(
        subject: str = '', 
        message_greeting: str='', 
        message_body: str='', 
        message_footer: str='', 
        view_in_browser_url: str='', 
        email_from: str='', 
        email_from_name: str='', 
        email_to = [], 
        reply_to: str='', 
        reply_to_name: str='',
    ):
    '''
    message
    '''

    try:

        variables = {
            'logo': '',
            'cover_image': '',
            'message_greeting': message_greeting.strip(),
            'message_body': message_body,
            'view_in_browser_url': view_in_browser_url.strip(),
            'message_footer': message_footer.strip(),
            'facebook': '',
            'twitter': '',
            'instagram': '',
            'linkedin': '',
            'site_name': '',
            'site_ts_and_cs': '',
            'site_faq': '',
            'site_unsubscribe': '',
        }

        if email_to == []:
            return ValidationError('Recipient email is needed')


        if email_from == '':
            return ValidationError('Email from is needed')
            
        if email_from_name != '':
            email_from = email_from_name.strip() + ' ' + ' <' + email_from + '>'
        

        if reply_to == '':
            reply_to = email_from
        
        if reply_to_name != '':
            reply_to = reply_to_name.strip() + ' ' + ' <' + reply_to + '>'

        message = EmailMultiAlternatives(
            subject=subject.strip(), 
            body=message_body, 
            from_email=email_from, 
            to=email_to, 
            headers={'Reply-To': reply_to}
        )
        
        message.attach_alternative(render_to_string('default.html', variables), 'text/html')

        return message.send()

        # msg = EmailMultiAlternatives(
        #     subject="Djrill Message",
        #     body="This is the text email body",
        #     from_email="Sender <djrill@example.com>",
        #     # to=["Recipient One <someone@example.com>", "another.person@example.com"],
        #     to=["Recipient One <recipient@example.com>", ],
        #     headers={'Reply-To': "Service <support@example.com>"} # optional extra headers
        # )
        # msg.attach_alternative("<p>This is the HTML email body</p>", "text/html")
        #
        # # Optional Mandrill-specific extensions:
        # msg.tags = ["one tag", "two tag", "red tag", "blue tag"]
        # msg.metadata = {'user_id': "8675309"}

    except Exception as e:
        print(e)
        raise ValidationError(e)
