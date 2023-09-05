from django.urls import path
from misstaffportal.views import (
    dashboard,
    appointment_detail,
    generate_job_order_form_small,
    appointment_update,
    view_appointment_admin,
    create_appointment_admin,
    update_servicerequest,
    generate_job_order_form_detail,
    delete_data
)

from users.views import (
    signup_view_admin,
    view_all_account_admin,
    view_acount_detail_admin
)


urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('appointment/<int:appointment_id>/', appointment_detail, name='appointment_detail'),
    path('appointment_update/<int:appointment_id>/', appointment_update, name='appointment_update'),
    path('update_servicerequest/<int:appointment_id>/', update_servicerequest, name='update_servicerequest'),
    path('delete_data/<int:appointment_id>/', delete_data, name='delete_data'),  # Add this URL pattern for data deletion

    path('generate_job_order_form_small/<int:appointment_id>/', generate_job_order_form_small, name='generate_job_order_form_small'),
    path('generate_job_order_form_detail/<int:appointment_id>/', generate_job_order_form_detail, name='generate_job_order_form_detail'),

    path('view_appointment_admin/', view_appointment_admin, name='view_appointment_admin'),
    path('create_appointment_admin/', create_appointment_admin, name='create_appointment_admin'),

    path('signup_view_admin/', signup_view_admin, name='signup_view_admin'),

    path('view_all_account_admin/', view_all_account_admin, name='view_all_account_admin'),
    path('view_acount_detail_admin/<int:pk>/', view_acount_detail_admin, name='view_acount_detail_admin'),
]
