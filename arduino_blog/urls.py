from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url

from . import views

app_name = 'arduino_blog'
urlpatterns = [
	url(r'^logout/$', views.user_logout, name="user_logout"),
	url(r'^activate/(?P<key>.+)$', views.activate_user, name="activate"),
    url(r'^new_activation/$', views.new_activation, name='new_activation'),
	url(r'^submit-abstract/$', views.submitabstract, name='submitabstract'),
    url(r'^register/$', views.user_register, name='user_register'),
    url(r'^login/$', views.user_login, name='user_login'),
	url(r'^$', views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)