from django.urls import path
from django.conf.urls import handler404
from .views import home, contact, coming_soon

handler404 = 'bloo_project.views.handler404'

urlpatterns = [
    path("", home, name="home"),
    path('contact/', contact, name='contact'),
    path('coming-soon/', coming_soon, name='coming_soon'),
]
