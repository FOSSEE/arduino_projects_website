from django.shortcuts import render, redirect
from django.conf import settings
from arduino_blog.models import Proposal
from django.db.models import Q

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
        except Exception as e:
            print (e)
            return redirect('/')
    return is_email_verified


def is_proposal_submitted(func):
    def is_submitted(request, *args, **kwargs):
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
                else:
                    _q = Proposal.objects
                    _q = _q.filter(Q(user_id=user.id)&Q(proposal_status='0'))
                    _q = _q.values('proposal_status')
                    _q = _q.order_by('proposal_status');
                    is_sub = _q.all()[:1]
                    if is_sub == 0:
                        context['success'] = True
                        context['msg'] = "You have alredy submited a \
                                            proposal"
                        return render(
                            request, 'dashboard.html', context
                        )
                    else:
                        context['success'] = False
                        context['msg'] = "You can submit a new \
                                            proposal"
                        return render(
                            request, 'dashboard.html', context
                        )
            return func(request, *args, **kwargs)
        except Exception as e:
            print (e)
            return redirect('/')
    return is_submitted
