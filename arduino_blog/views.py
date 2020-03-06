from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.template import loader
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import (csrf_exempt, csrf_protect,
                                          ensure_csrf_cookie,
                                          requires_csrf_token)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from arduino_blog.forms import UserRegistrationForm, AbstractProposalForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from arduino_blog.models import Proposal, Profile, Comment
from .send_emails import (send_user_mail,
                          generate_activation_key)
from django.utils import timezone
from arduino_projects_website.settings import URL_ROOT
from .decorators import email_verified, is_proposal_submitted
from django.core.mail import EmailMultiAlternatives
import datetime

def my_redirect(url):
    """An overridden redirect to deal with URL_ROOT-ing. See settings.py
    for details."""
    return redirect(URL_ROOT + url)

def my_render_to_response(request, template, context=None, **kwargs):
    """Overridden render_to_response.
    """
    if context is None:
        context = {'URL_ROOT': URL_ROOT}
    else:
        context['URL_ROOT'] = URL_ROOT
    return render(request, template, context, **kwargs)


def user_logout(request):
    """Show a page to inform user that the quiz has been compeleted."""
    logout(request)
    return redirect('/')

#view to landing page
def index(request):
    context = {}
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

@csrf_protect
def user_register(request):
    '''User Registration form'''
    user = request.user
    if user.is_authenticated:
        return my_redirect("/submit-abstract")
    context = {}
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            u_name, pwd, user_email, key = form.save()
            new_user = authenticate(username=u_name, password=pwd)
            login(request, new_user)
            if user_email and key:
                success, msg = send_user_mail(user_email, key)
                #msg = 'Hello'
                context = {'activation_msg': msg}
                return my_render_to_response(
                    request,
                    'activation-status.html', context
                )
            return index(request)
        else:
            return my_render_to_response(
                request, 'user-register.html', {'form': form}
            )
    else:
        form = UserRegistrationForm()
        return my_render_to_response(
            request, 'user-register.html', {'form': form}
        )

@requires_csrf_token
def user_login(request):
    user = request.user
    context = {}
    if request.user.is_authenticated:
        return render(request, 'index.html', context)
    else:
        if request.method == "POST":
            context = {}
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                proposals = Proposal.objects.filter(user=request.user).count()
                context['user'] = user
                #context['cfp_dates'] = 'August 20'
                return redirect('/submit-abstract')
                #template = loader.get_template('index.html')
                #return render(request, 'index.html', context)
            else:
                context['invalid'] = True
                context['form'] = UserLoginForm
                context['user'] = user
                #context['cfp_dates'] = 'August 20'
                #context['proposals_a'] = proposals_a
                return render(request, 'login.html', context)
        else:
            form = UserLoginForm()
            context = {'request': request,
                       'user': request.user,
                       'form': form,
                    }
            template = loader.get_template('login.html')
            return HttpResponse(template.render(context, request))

def activate_user(request, key):
    profile = get_object_or_404(Profile, activation_key=key)
    context = {}
    context['success'] = False
    if profile.is_email_verified:
        context['activation_msg'] = "Your account is already verified"
        return my_render_to_response(
            request, 'activation-status.html', context
        )

    if timezone.now() > profile.key_expiry_time:
        context['msg'] = dedent("""
                    Your activation time expired.
                    Please try again.
                    """)
    else:
        context['success'] = True
        profile.is_email_verified = True
        profile.save()
        context['msg'] = "Your account is activated"
    return my_render_to_response(
        request, 'activation-status.html', context
    )


def new_activation(request, email=None):
    context = {}
    if request.method == "POST":
        email = request.POST.get('email')

    try:
        user = User.objects.get(email=email)
    except MultipleObjectsReturned:
        context['email_err_msg'] = "Multiple entries found for this email"\
                                    "Please change your email"
        return my_render_to_response(
            request, 'activation-status.html', context
        )
    except ObjectDoesNotExist:
        context['success'] = False
        context['msg'] = "Your account is not verified. \
                            Please verify your account"
        return my_render_to_response(
            request, 'activation-status.html', context
            )

    if not user.profile.is_email_verified:
        user.profile.activation_key = generate_activation_key(user.username)
        user.profile.key_expiry_time = timezone.now() + \
            timezone.timedelta(minutes=60)
        user.profile.save()
        new_user_data = User.objects.get(email=email)
        success, msg = send_user_mail(new_user_data.email,
                                      new_user_data.profile.activation_key
                                      )
        if success:
            context['activation_msg'] = msg
        else:
            context['msg'] = msg
    else:
        context['activation_msg'] = "Your account is already verified"

    return my_render_to_response(
        request, 'activation-status.html', context
    )


@csrf_protect
@login_required
@email_verified
@is_proposal_submitted
def submitabstract(request):
    context = {}
    if request.user.is_authenticated:
        social_user = request.user
        django_user = User.objects.get(username=social_user)
        context['user'] = django_user
        if request.method == 'POST':
            form = AbstractProposalForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = django_user
                data.name_of_author = social_user.first_name + ' ' + social_user.last_name
                data.email = social_user.email
                data.attachment = request.FILES
                data.proposal_status = 0
                data.approval_date = datetime.date.today()
                data.save()
                context['proposal_submit'] = True
                context['display_message'] = """Thank you for your submission! """
                #mail function
                context['name'] = social_user.first_name + ' ' + social_user.last_name
                subject = ["test mail"]
                message = render_to_string('email/proposal_received.html',\
                        context)
                print(message)
                sender_email = [SENDER_EMAIL]
                to = [social_user.email]
                bcc_email = [BCC_EMAIL_ID]
                send_email(sender_email, to, subject, message, bcc_email)
                return my_render_to_response('index.html', context)
            else:
                print(form.errors)
                context['proposal_form'] = form
                #context['proposals_a'] = proposals_a
                template = loader.get_template('submit-cfp.html')
                return HttpResponse(template.render(context, request))
        else:
            form = AbstractProposalForm()
            return render(request, 'submit-cfp.html', {'proposal_form': form})
    else:
        context['login_required'] = True
        return my_render_to_response('login.html', context)


def send_email(sender_email, to, subject, message, bcc_email=None):
    email = EmailMultiAlternatives(
        subject, '',
        sender_email, to,
        bcc=[bcc_email],
        headers={"Content-type": "text/html;charset=iso-8859-1"}
    )
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'  # Main content is text/html
    email.mixed_subtype = 'related'
    print("mail sent")
    email.send(fail_silently=True)

@login_required
@csrf_protect
def view_abstracts(request):
    user = request.user
    context = {}
    count_list = []
    if request.user.is_authenticated:
        if user.is_staff:
            proposals = Proposal.objects.all()
            context['proposals'] = proposals
            context['user'] = user
            return render(request, 'view-proposals.html', context)
        elif user is not None:
            if Proposal.objects.filter(user=user).exists:
                proposals = Proposal.objects.filter(
                    user=user)
                context['counts'] = count_list
                context['proposals'] = proposals
                context['user'] = user
            return render(request, 'view-proposals.html', context)
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html', context)

@login_required
def abstract_details(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        if user.is_staff:
            comments = Comment.objects.filter(object_id = proposal_id)
            context['comments'] = comments
            proposal = Proposal.objects.get(id=proposal_id)
            context['proposal'] = proposal
            context['user'] = user
            return render(request, 'comment-abstract.html', context)
        elif user is not None:
            try:
                proposal = Proposal.objects.get(id=proposal_id)
                comments = Comment.objects.filter(object_id= proposal_id)
                if proposal.user == user:
                    try:
                        context['proposal'] = proposal
                        context['comments'] = comments
                    except:
                        pass
                    context['comments'] = comments
                    context['proposal'] = proposal
                    context['user'] = user
                    return render(request, 'abstract-details.html', context)
                else:
                    return render(request, 'home.html', context)
            except:
                return render(request, 'abstract-details.html', context)
        else:
            return render(request, 'home.html', context)
    else:
        return render(request, 'home.html', context)

@login_required
def comment_abstract(request, proposal_id=None):
    user = request.user
    context = {}
    if user.is_authenticated:
        if user.is_staff:
            try:
                proposal = Proposal.objects.get(id=proposal_id)
                if request.method == 'POST':
                    #comment = Comment()
                    text = request.POST.get('comment')
                    #comment.user = user
                    comment = Comment.objects.create(content_object=proposal, body = text,  user=request.user)
                    comment.save()
                    proposal.status = "Commented"
                    proposal.save()
                    comments = Comment.objects.filter(user= request.user)
                    context['proposal'] = proposal
                    context['comments'] = comments
                    template = loader.get_template('comment-abstract.html')
                    return HttpResponse(template.render(context, request))
                else:
                    comments = Comment.objects.filter(user=user)
                    context['proposal'] = proposal
                    context['comments'] = comments
                    template = loader.get_template('comment-abstract.html')
                    return HttpResponse(template.render(context, request))
            except:
                template = loader.get_template('comment-abstract.html')
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('comment-abstract.html')
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('comment-abstract.html')
        return HttpResponse(template.render(context, request))     