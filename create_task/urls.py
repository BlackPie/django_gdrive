from django.conf.urls import include, url
from django.contrib import admin

from create_task.apps.gdrive import views


urlpatterns = [
    url(r'^$', views.DocumentListView.as_view(), name='document_list'),
    url(r'^register/$', views.RegisterFormView.as_view(), name="register"),
    url(r'^login/$', views.LoginFormView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    url(r'^create_document/$', views.DocumentCreateView.as_view(), name="create_document"),
    url('^update_document/(?P<pk>\d+)$', views.DocumentUpdateView.as_view(), name='update_document'),
    url(r'^oauth/$', views.OAuthView.as_view(), name="oauth"),

    url(r'^admin/', include(admin.site.urls)),
]
