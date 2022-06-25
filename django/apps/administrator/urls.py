
from django.conf.urls import url
from django.contrib import admin

from apps.administrator import views

urlpatterns = [
    url(r'^$', views.AdminViewSet.as_view(), name='administrator_admin'),
    url(r'^dashboard/$', views.AdminDashboardViewSet.as_view(), name='administrator_dashboard'),
    url(r'^landing/$', views.Landing.as_view(), name='administrator_landing'),
]