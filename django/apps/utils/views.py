from django.shortcuts import render
from django.apps import apps
# Create your views here.

from werkzeug.urls import url_parse
from random import randint, choice

import string
import urllib.parse
import socket
import hashlib


def get_field_choices(named):
    """
    Get choices from namedtuple
    """
    dictionary = named._asdict()
    return [(v, k) for (k, v) in dictionary.items()]


def random_generator(length=5, letters=True, digits=False, punctuation=False, exclude=[]):
    '''
    Create random string
    leave_out - list of string charecters to leave out e.g [':', '<', '8'] 
    '''
    
    allchar = ''

    if letters:
        # allchar = string.ascii_letters 
        allchar = string.ascii_uppercase 
    if digits:
        allchar += string.digits 
    if punctuation:
        allchar += string.punctuation

    if not letters and not digits and not punctuation:
        # allchar = string.ascii_letters 
        allchar = string.ascii_uppercase 

    generator = "".join(choice(allchar) for x in range(randint(length, length)) if str(x) not in exclude)
    
    return generator
    
# def check_if_object_exists(app_label=None, model_name=None, field_name=None, object=None):
#     """
#     Check if object exists in a table based on field name
#     """

#     try:
#         model = apps.get_model(app_label=app_label, model_name=model)
#         field = model._meta.get_field('field_name')
#         # field.value_from_object(object)
#         if getattr(object, ):
#             return True
#         else:
#             return False
#     except:
#         return False


#     if model_name:
#         if check_if_object_exists(app_label=None, model_name=None, field_name=None, object=generator):
#             return random_generator(length=length, letters=letters, digits=digits, punctuation=punctuation, replace=replace, app_label=app_label, model=model)
    
#     return generator

def pf_payment_data(merchant_id='', merchant_key='', return_url='', cancel_url='', notify_url='', name_first=None, name_last=None, email_address='', m_payment_id='', amount='', item_name=''):
    '''
    payfast payload
    '''
    data = {
        # Merchant details
        'merchant_id': merchant_id,
        'merchant_key': merchant_key,
        'return_url': return_url,
        'cancel_url': cancel_url,
        'notify_url': notify_url,
        # Buyer details
        'name_first': name_first,
        'name_last': name_last,
        'email_address': email_address,
        # Transaction details
        'm_payment_id': m_payment_id, #Unique payment ID to pass through to notify_url
        'amount': amount,
        'item_name': item_name
    }

    # Generate signature (see step 2)
    signature = generateSignature(data)
    data['signature'] = signature

    return data

def generateSignature(dataArray, passPhrase = ''):
    payload = ""
    for key in dataArray:
        # Get all the data from PayFast and prepare parameter string
        payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    payload = payload[:-1]
    if passPhrase != '':
        payload += f"&passphrase={passPhrase}"
    return hashlib.md5(payload.encode()).hexdigest()

def pfValidSignature(postData, signature):

    SANDBOX_MODE = True

    pfHost = 'sandbox.payfast.co.za' if SANDBOX_MODE else 'www.payfast.co.za'

    # Get posted variables from ITN and convert to a string
    pfData = postData
    # postData = postData.decode().split('&')
    # for i in range(0,len(postData)):
    #     splitData = postData[i].split('=')
    #     pfData[splitData[0]] = splitData[1]

    pfParamString = ""
    for key in pfData:
    # Get all the data from PayFast and prepare parameter string
        if key != 'signature':
            pfParamString += key + "=" + urllib.parse.quote_plus(pfData[key].replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    # payload += "passphrase=SecretPassphrase123"
    pfParamString = pfParamString[:-1] 

    # Generate our signature from PayFast parameters
    verify_signature = hashlib.md5(pfParamString.encode()).hexdigest()
    
    return (signature == verify_signature)

def validIP(headers):

    valid_hosts = [
        'www.payfast.co.za',
        'sandbox.payfast.co.za',
        'w1w.payfast.co.za',
        'w2w.payfast.co.za',
        'www.airbuy.africa',
        'airbuy.africa',
    ]
    valid_ips = []

    for item in valid_hosts:
        ips = socket.gethostbyname_ex(item)
        if ips:
            for ip in ips:
                if ip:
                    valid_ips.append(ip)
                    
    # Remove duplicates from array
    clean_valid_ips = []
    for item in valid_ips:
        # Iterate through each variable to create one list
        if isinstance(item, list):
            for prop in item:
                if prop not in clean_valid_ips:
                    clean_valid_ips.append(prop)
        else:
            if item not in clean_valid_ips:
                clean_valid_ips.append(item)
    
    clean_valid_ips.append("localhost:8080")

    # Security Step 3, check if referrer is valid
    # request.headers.get("Referer")
    if url_parse(headers.get("Referer", 'https://google.com/')).host in clean_valid_ips:
        return True 
    else:
        return False