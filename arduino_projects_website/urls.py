"""arduino_projects_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    re_path(r'^', include('arduino_blog.urls', namespace='arduino_blog')),
    re_path(r'^accounts/',
            include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
    
    # URLs for password reset and password change
    re_path('^accounts/forgotpassword/', auth_views.PasswordResetView.as_view(\
    template_name= 'registration/password_reset_form.html'),\
    name = "password_reset"),

    re_path(r'^accounts/password_reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$',\
    auth_views.PasswordResetConfirmView.as_view(\
    template_name= 'registration/password_reset_confirm.html'\
    ), name = 'password_reset_confirm'),

    re_path(r'^accounts/password_reset/mail_sent/', \
    auth_views.PasswordResetDoneView.as_view(template_name= \
    'registration/password_reset_done.html'),\
    name = 'password_reset_done'),

    re_path(r'^accounts/password_reset/complete/', auth_views.\
    PasswordResetCompleteView.as_view(template_name= \
    'registration/password_reset_complete.html'),\
    name = 'password_reset_complete'),

    re_path(r'^accounts/changepassword/', auth_views.PasswordChangeView.as_view(\
    template_name='registration/password_change_form.html'\
    ), name = 'password_change'),

    re_path(r'^accounts/password_change/done/', auth_views.\
    PasswordChangeDoneView.as_view(template_name= \
    'registration/password_change_done.html'),\
    name = 'password_change_done'),

]
