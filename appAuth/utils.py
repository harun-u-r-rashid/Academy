import random
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from . import models




def generate_otp():
        return ''.join(random.choices('1234567890', k=7))



def send_code_to_activate_user_account(email):
        try:
                otp_code = generate_otp()
                user = models.User.objects.get(email=email)

                otp_object = models.OneTimePassword.objects.create(user=user, code = otp_code)
                otp_object.save()


                email_subject = "Please active your account."
                email_body = render_to_string('otp_email.html', {'otp_code':otp_code})

                email_message = EmailMultiAlternatives(email_subject,'', to=[user.email])
                email_message.attach_alternative(email_body, 'text/html')
                email_message.send()

        except Exception as e:
                return f"Failed to send OTP to {email} : {str(e)}"
        
