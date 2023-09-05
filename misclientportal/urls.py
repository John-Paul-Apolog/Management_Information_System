from django.urls import path
from misclientportal.views import create_appointment, view_appointment
from users.views import user_logout, verification_views

urlpatterns = [
    path('appointment/', create_appointment, name='appointment'),
    path('view_appointment/', view_appointment, name='view_appointment'),
    path('user_logout', user_logout, name='user_logout'),
    path('verification_views/', verification_views, name='verification_views'),
]