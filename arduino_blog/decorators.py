from django.shortcuts import render, redirect
from django.conf import settings

def email_verified(func):
    """
    This decorator is used to check if email is verified.
    If email is not verified then redirect user for email
    verification.
    """

    def is_email_verified(request, *args, **kwargs):
        user = request.user
        context = {}
        try:
            if user.is_authenticated:
                if not user.profile.is_email_verified:
                    context['success'] = False
                    context['msg'] = "Your account is not verified. \
                                        Please verify your account"
                    return render(
                        request, 'activation-status.html', context
                    )
            return func(request, *args, **kwargs)
        except:
            return redirect('/')
    return is_email_verified
