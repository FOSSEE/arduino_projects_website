from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url

from . import views

app_name = 'arduino_blog'
urlpatterns = [
    re_path(r'^comment-abstract/(?P<proposal_id>\d+)$',
    	views.comment_abstract, name='comment_abstract'),
	re_path(r'^abstract-details/(?P<proposal_id>\d+)$', 
		views.abstract_details, name='abstract_details'),
	url(r'^view-abstracts/$', views.view_abstracts, name="view_abstracts"),
	url(r'^accounts/logout/$', views.user_logout, name="user_logout"),
	url(r'^activate/(?P<key>.+)$', views.activate_user, name="activate"),
    url(r'^new_activation/$', views.new_activation, name='new_activation'),
	url(r'^submit-abstract/$', views.submitabstract, name='submitabstract'),
    url(r'^accounts/register/$', views.user_register, name='user_register'),
    url(r'^accounts/login/$', views.user_login, name='user_login'),
	url(r'^$', views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
