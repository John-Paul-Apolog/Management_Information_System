from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm
from django.http import HttpResponse
from .models import Appointment
from users.models import VerifiedAccount
from misstaffportal.models import ServiceRequest

@login_required
def create_appointment(request):
    user = request.user
    verified_account = VerifiedAccount.objects.filter(user=user).first()
    if not verified_account or not verified_account.is_verified:
        return redirect('verification_views')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.notes = 'None'
            appointment.user = request.user
            appointment.save()

            # Create a ServiceRequest record and associate it with the created Appointment record
            service_request = ServiceRequest.objects.create(
                department='Example Department',
                service_type='repair',
                scheduled_response_date='2022-01-01',
                scheduled_response_time='09:00',
                verified_by_client=False,
                problem_found='Example problem',
                recommendation='Example recommendation',
                service_completed_date='2022-01-02',
                service_verified_by_client_date='2022-01-03',
                appointment=appointment
            )

            messages.success(request, 'Your appointment has been created!')
            return redirect('view_appointment')
    else:
        form = AppointmentForm()
    return render(request, 'misclientportal/create_appointment.html', {'form': form})

@login_required
def view_appointment(request):
    user = request.user
    verified_account = VerifiedAccount.objects.filter(user=user).first()
    if not verified_account or not verified_account.is_verified:
        return redirect('verification_views')
    # Retrieve all appointments for the current user
    appointments = Appointment.objects.filter(user=request.user).order_by('-timestamp')

    # Create a list of appointment data to pass to the template
    appointment_data = []
    for appointment in appointments:
        data = {
            'id': appointment.id,
            'full_name': appointment.full_name,
            'device_type': appointment.device_type,
            'device_model': appointment.device_model,
            'issue_description': appointment.issue_description,
            'appointment_date': appointment.appointment_date,
            'status': appointment.status,
        }
        appointment_data.append(data)

    # Render the template with the appointment data
    return render(request, 'misclientportal/view_appointment.html', {'appointment_data': appointment_data})

# Create your views here.
