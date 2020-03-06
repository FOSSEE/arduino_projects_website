from django import forms

from django.forms import ModelForm, widgets

import datetime
from dateutil.relativedelta import relativedelta

from django.utils import timezone

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, \
    RegexValidator, URLValidator
from captcha.fields import ReCaptchaField
from string import punctuation, digits
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters

#from arduino_blog.models import Proposal
#from arduino_blog.send_mails import generate_activation_key
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from arduino_blog.models import (
    Profile, User, Proposal, Comment
)
from .send_emails import (send_user_mail,
                          generate_activation_key)
from arduino_blog.views import *

UNAME_CHARS = letters + "._" + digits
PWD_CHARS = letters + punctuation + digits
MY_CHOICES = (
    ('Beginner', 'Beginner'),
    ('Advanced', 'Advanced'),
)

ws_duration = (
    ('2', '2'),
    ('3', '3'),
)
abs_duration = (
    ('15', '15'),
)


MY_CHOICES = (
    ('Beginner', 'Beginner'),
    ('Advanced', 'Advanced'),
)
rating = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
)

CHOICES = [('1', 'Yes'),
           ('0', 'No')]

position_choices = (
    ("student", "Student"),
    ("faculty", "Faculty")
)

source = (
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("NMEICT Blended Workshop", "NMEICT Blended Workshop"),
    ("From other College", "From other College"),
)

title = (
    ("Mr", "Mr."),
    ("Miss", "Ms."),
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
)
states = (
    ("IN-AP",    "Andhra Pradesh"),
    ("IN-AR",    "Arunachal Pradesh"),
    ("IN-AS",    "Assam"),
    ("IN-BR",    "Bihar"),
    ("IN-CT",    "Chhattisgarh"),
    ("IN-GA",    "Goa"),
    ("IN-GJ",    "Gujarat"),
    ("IN-HR",    "Haryana"),
    ("IN-HP",    "Himachal Pradesh"),
    ("IN-JK",    "Jammu and Kashmir"),
    ("IN-JH",    "Jharkhand"),
    ("IN-KA",    "Karnataka"),
    ("IN-KL",    "Kerala"),
    ("IN-MP",    "Madhya Pradesh"),
    ("IN-MH",    "Maharashtra"),
    ("IN-MN",    "Manipur"),
    ("IN-ML",    "Meghalaya"),
    ("IN-MZ",    "Mizoram"),
    ("IN-NL",    "Nagaland"),
    ("IN-OR",    "Odisha"),
    ("IN-PB",    "Punjab"),
    ("IN-RJ",    "Rajasthan"),
    ("IN-SK",    "Sikkim"),
    ("IN-TN",    "Tamil Nadu"),
    ("IN-TG",    "Telangana"),
    ("IN-TR",    "Tripura"),
    ("IN-UT",    "Uttarakhand"),
    ("IN-UP",    "Uttar Pradesh"),
    ("IN-WB",    "West Bengal"),
    ("IN-AN",    "Andaman and Nicobar Islands"),
    ("IN-CH",    "Chandigarh"),
    ("IN-DN",    "Dadra and Nagar Haveli"),
    ("IN-DD",    "Daman and Diu"),
    ("IN-DL",    "Delhi"),
    ("IN-LD",    "Lakshadweep"),
    ("IN-PY",    "Puducherry")
)


class UserRegistrationForm(forms.Form):
    """A Class to create new form for User's Registration.
    It has the various fields and functions required to register
    a new user to the system"""
    required_css_class = 'required'
    errorlist_css_class = 'errorlist'
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), max_length=32, help_text='''Letters, digits,
                               period and underscore only.''',)
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'placeholder': 'Enter valid email id'}))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=32, label='First name', widget=forms.TextInput(
        attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=32, label='Last name', widget=forms.TextInput(
        attrs={'placeholder': 'Last name'},))
    institute = forms.CharField(max_length=32, 
        label='Institute/Organization/Company', widget=forms.TextInput())
    position = forms.ChoiceField(choices = position_choices)
    # department = forms.ChoiceField(help_text='Department you work/study',
    #             choices=department_choices)
    state = forms.ChoiceField(choices=states)
    city = forms.CharField(max_length=255, help_text="Enter the city")
    pincode = forms.CharField(max_length=6, help_text="Enter the pincode")
    how_did_you_hear_about_us = forms.ChoiceField(
        choices=source, label='How did you hear about us?')

    def clean_username(self):
        u_name = self.cleaned_data["username"]
        if u_name.strip(UNAME_CHARS):
            msg = "Only letters, digits, period  are"\
                  " allowed in username"
            raise forms.ValidationError(msg)
        try:
            User.objects.get(username__exact=u_name)
            raise forms.ValidationError("Username already exists.")
        except User.DoesNotExist:
            return u_name

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if pwd.strip(PWD_CHARS):
            raise forms.ValidationError("Only letters, digits and punctuation\
                                        are allowed in password")
        return pwd

    def clean_confirm_password(self):
        c_pwd = self.cleaned_data['confirm_password']
        pwd = self.data['password']
        if c_pwd != pwd:
            raise forms.ValidationError("Passwords do not match")

        return c_pwd

    def clean_email(self):
        user_email = self.cleaned_data['email']
        if User.objects.filter(email=user_email).exists():
            raise forms.ValidationError("This email already exists")
        return user_email

    def save(self):
        u_name = self.cleaned_data["username"]
        u_name = u_name.lower()
        pwd = self.cleaned_data["password"]
        email = self.cleaned_data["email"]
        new_user = User.objects.create_user(u_name, email, pwd)
        new_user.first_name = self.cleaned_data["first_name"]
        new_user.last_name = self.cleaned_data["last_name"]
        new_user.save()

        cleaned_data = self.cleaned_data
        new_profile = Profile(user=new_user)
        new_profile.institute = cleaned_data["institute"]
        new_profile.position = cleaned_data["position"]
        new_profile.pincode = cleaned_data["pincode"]
        new_profile.city = cleaned_data["city"]
        new_profile.state = cleaned_data["state"]
        new_profile.how_did_you_hear_about_us = cleaned_data["how_did_you_hear_about_us"]
        new_profile.activation_key = generate_activation_key(
                new_user.username)
        new_profile.key_expiry_time = timezone.now() + timezone.timedelta(
                minutes=60)
        new_profile.save()
        return u_name, pwd, new_user.email, new_profile.activation_key

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-inline', 'placeholder': 'Username'}),
        label='User Name'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-inline', 'placeholder': 'Password'}),
        label='Password'
    )

class AbstractProposalForm(forms.ModelForm):
    # name_of_author = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the name of first author'}),
    #                         required=True,
    #                         error_messages={
    #                             'required': 'Name of Author field required.'},
    #                         )
    about_the_author = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'About Me'}),
                               required=True,
                               error_messages={
                                   'required': 'About the author field required.'},
                               )
    # attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
    #                              label='Please upload relevant documents (if any)',
    #                              required=False,)
    title_of_the_project = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title of the Project'}),
                            required=True,
                            error_messages={
                                'required': 'Title field required.'},
                            )
    abstract = forms.CharField(min_length=300,  widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Abstract', 'onkeyup': 'countChar(this)'}),
                               required=True,
                               label='Abstract (Min. 300 char.)',
                               error_messages={
                                   'required': 'Abstract field required.'},
                               )
    references = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'References(if any)'})
                            )
    completion_date = forms.DateTimeField(
            input_formats=['%YY-%mm-%dd'],
            widget=forms.DateTimeInput(attrs={
                'class': 'form-control datetimepicker-input',
                'data-target': '#datetimepicker1'
            })
        )

    terms_and_conditions = forms.BooleanField(widget=forms.CheckboxInput(), 
        required=True, label='I agree to the terms and conditions')

    class Meta:
        model = Proposal
        exclude = ('user','name_of_author', 'email', 'status', 'rate','proposal_status', 'approval_date')


    def __init__(self, *args, **kwargs):
        super(AbstractProposalForm, self).__init__(*args, **kwargs)
        self.fields['completion_date'].disabled = True
        self.fields['completion_date'].initial = (datetime.date.today() + relativedelta(months=1))