from django.urls import path
from users.views import signup_view, verification_views, login_views, index, user_logout, resend_verification_code
from misclientportal.views import create_appointment
from misstaffportal.views import dashboard

urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup_view, name='signup_views'),
    path('verification_views/', verification_views, name='verification_views'),
    path('resend_verification_code/', resend_verification_code, name='resend_verification_code' ),
    path('login/', login_views, name='login_views'),
    path('logout/', user_logout, name='user_logout'),
    
    path('create_appointment/', create_appointment, name='create_appointment'),

    path('dashboard/', dashboard, name='dashboard'),
]
