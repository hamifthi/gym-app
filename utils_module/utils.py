from django.conf import settings

import requests
import os, binascii

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def google_recaptcha_verify(request):
    captcha_response = request.POST.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_response,
        'remoteip': get_client_ip(request)
    }
    verify_response = requests.post(url=url, params=params, verify=True)
    verify_response = verify_response.json()
    return verify_response.get("success",)

def user_recaptcha_fails(request):
    if 'g-recaptcha-response' in request.POST:
            if not google_recaptcha_verify(request):
                return True
    else:
        return True

def random_code():
        return binascii.b2a_hex(os.urandom(24)).decode('utf-8')

if __name__ == '__main__':
    pass