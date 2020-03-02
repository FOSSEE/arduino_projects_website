from django.db import models
from django.contrib.auth.models import User
from social.apps.django_app.default.models import UserSocialAuth
from django.core.validators import RegexValidator
import os
from datetime import datetime
from arduino_projects_website import settings

position_choices = (
    ("student", "Student"),
    ("faculty", "Faculty")
)

gender = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

source = (
    ("Poster", "Poster"),
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


""" Base class created to collect creation date and modified date. Can be inherited in the other models """
class BaseClass(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Profile(BaseClass):
    """Profile for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=32, blank=True, choices=title)
    institute = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)
    position = models.CharField(max_length=32, choices=position_choices)
    how_did_you_hear_about_us = models.CharField(
        max_length=255, blank=True, choices=source)
    state = models.CharField(max_length=50, choices = states, blank=True)
    city = models.CharField(max_length=50, blank= True)
    pincode = models.CharField(max_length=6, blank =True)
    is_email_verified = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=255, blank=True, null=True)
    key_expiry_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return u"id: {0}| {1} {2} | {3} ".format(
            self.user.id,
            self.user.first_name,
            self.user.last_name,
            self.user.email
        )

def get_document_dir(instance, filename):
    # ename, eext = instance.user.email.split("@")
    fname, fext = os.path.splitext(filename)
    # print "----------------->",instance.user
    return '%s/attachment/%s/%s.%s' % (instance.user, instance.proposal_type, fname+'_'+str(instance.user), fext)

class Proposal(BaseClass):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    name_of_author = models.CharField(max_length=200, default='None')
    about_the_author = models.TextField(max_length=500)
    email = models.CharField(max_length=128)
    title_of_the_project = models.CharField(max_length=250)
    abstract = models.TextField(max_length=700)
    attachment = models.FileField(upload_to=get_document_dir)
    status = models.CharField(max_length=100, default='Pending', editable=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    proposal_status = models.IntegerField(default=0, editable=True)
    #tags = models.CharField(max_length=250)
    terms_and_conditions = models.BooleanField(default= 'True')
