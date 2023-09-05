import datetime
import io
import os


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
from django.contrib import messages
from django.contrib import messages

from misclientportal.models import Appointment
from users.models import VerifiedAccount
from .forms import AppointmentNotesForm
from .forms import AppointmentUpdateForm
from .forms import AppointmentForm
from .forms import ServiceRequestForm
from .models import ServiceRequest
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from datetime import datetime
from reportlab.pdfbase.pdfmetrics import stringWidth

def check_verified_account(user):
    verified_account = VerifiedAccount.objects.filter(user=user).first()
    if not verified_account or not verified_account.is_verified:
        return False
    return True

def redirect_unverified(request):
    return redirect('verification_views')

def get_recent_appointments():
    appointments = Appointment.objects.order_by('-timestamp')[:5]
    return appointments

def get_all_appointments():
    appointments = Appointment.objects.order_by('-timestamp')
    return appointments

def count_appointments_by_status(appointments):
    counts = {
        'pending_appointments': 0,
        'in_progress_appointments': 0,
        'completed_appointments': 0,
        'to_follow_up_appointments': 0,
    }
    
    for appointment in appointments:
        if appointment.status == 'PENDING':
            counts['pending_appointments'] += 1
        elif appointment.status == 'IN_PROGRESS':
            counts['in_progress_appointments'] += 1
        elif appointment.status == 'COMPLETED':
            counts['completed_appointments'] += 1
        elif appointment.status == 'TO_FOLLOW_UP':
            counts['to_follow_up_appointments'] += 1

    return counts

def count_appointments_by_month(appointments):
    months = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'Aug': 8,
        'Sept': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }
    
    counts = {}
    
    for month_name, month_number in months.items():
        month_appointments = appointments.filter(appointment_date__month=month_number)
        counts[month_name + '_pen'] = month_appointments.filter(status='PENDING').count()
        counts[month_name + '_pr'] = month_appointments.filter(status='IN_PROGRESS').count()
        counts[month_name + '_com'] = month_appointments.filter(status='COMPLETED').count()
        counts[month_name + '_tf'] = month_appointments.filter(status='TO_FOLLOW_UP').count()

    return counts

@login_required
def update_appointment_notes(appointment, form_data):
    form = AppointmentNotesForm(form_data, instance=appointment)
    if form.is_valid():
        form.save()

@login_required
def dashboard(request):

    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    all_appointments = get_all_appointments()
    appointment_counts = count_appointments_by_status(all_appointments)
    month_counts = count_appointments_by_month(all_appointments)
    recent_appointments = get_recent_appointments()

    context = {
        'recent_appointments': recent_appointments,
        **appointment_counts,
        **month_counts,
        'appointments': all_appointments,
    }

    return render(request, 'misstaffportal/Dashboard.html', context)

@login_required
def appointment_detail(request, appointment_id):
    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    appointment = get_object_or_404(Appointment, id=appointment_id)
    form = AppointmentNotesForm(instance=appointment)

    if request.method == 'POST':
        form = AppointmentNotesForm(request.POST, instance=appointment)
        if form.is_valid():
            update_appointment_notes(appointment, request.POST)
            return redirect('dashboard')  # Redirect to the dashboard after update

    all_appointments = get_all_appointments()
    appointment_counts = count_appointments_by_status(all_appointments)

    context = {
        **appointment_counts,
        'appointments': all_appointments,
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'misstaffportal/appointment_detail.html', context)

@login_required
def appointment_update(request, appointment_id):

    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_detail', appointment_id=appointment.id)  # Replace 'appointment_detail' with your actual URL pattern name for the appointment detail view
    else:
        form = AppointmentUpdateForm(instance=appointment)

    context = {
        'form': form,
        'appointment': appointment
    }
    return render(request, 'misstaffportal/update_appointment.html', context)

@login_required
def view_appointment_admin(request):
    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Retrieve all appointments from the database
    all_appointments = Appointment.objects.all().order_by('-timestamp')
    appointment_counts = count_appointments_by_status(all_appointments)

    context = {
        **appointment_counts,
        'appointments': all_appointments,
    }

    return render(request, 'misstaffportal/view_appointment.html', context)

@login_required
def create_appointment_admin(request):
    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
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
            return redirect('view_appointment_admin')
    else:
        form = AppointmentForm()
    
    return render(request, 'misstaffportal/create_appointment.html', {'form': form})

@login_required
def update_servicerequest(request, appointment_id):
    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the ServiceRequest record associated with the Appointment record with a matching appointment_id
    service_request = get_object_or_404(ServiceRequest, appointment_id=appointment_id)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, instance=service_request)
        if form.is_valid():
            service_request = form.save(commit=False)
            
            # Convert 'verified_by_client' value to a boolean
            verified_by_client = request.POST.get('verified_by_client', False) == 'True'
            service_request.verified_by_client = verified_by_client
            
            service_request.save()
            
            messages.success(request, 'The service request has been updated!')
            return redirect('update_servicerequest', appointment_id=appointment_id)
    else:
        form = ServiceRequestForm(instance=service_request)
    
    # Add appointment_id to the context dictionary
    context = {
        'form': form,
        'appointment_id': appointment_id
    }
    
    return render(request, 'misstaffportal/servicerequest_update.html', context)

def delete_data(request, appointment_id):

    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Delete the associated service request
    try:
        service_request = ServiceRequest.objects.get(appointment=appointment)
        service_request.delete()
    except ServiceRequest.DoesNotExist:
        pass

    # Delete the appointment
    appointment.delete()

    # Redirect to a desired page after deletion
    return redirect('dashboard')

@login_required
def generate_job_order_form_small(request, appointment_id):

    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create a PDF document object with the specified page size and no margins
    doc = SimpleDocTemplate(buffer, pagesize=(4.5 * inch, 6 * inch), leftMargin=3, rightMargin=3, topMargin=3, bottomMargin=3, title='Job Order Form', showBoundary=1)



    # Replace with your own context data
    context = {
        'data': 'MIS Job Order Form',
        'form_number': 'FM-MIS-05',
        'revision_date': datetime.now().strftime("%B %d, %Y")
    }

    # Create a list to hold the PDF elements
    elements = []

    # Create custom paragraph styles
    centered_style = ParagraphStyle(name='Centered', alignment=TA_CENTER, fontSize=15)
    right_style = ParagraphStyle(name='Right', alignment=TA_RIGHT, fontSize=7)
    left_style = ParagraphStyle(name='Left', alignment=TA_LEFT, fontSize=7)

    # Add elements to the list
    elements.append(Paragraph(context['form_number'], right_style))
    elements.append(Paragraph(f'REVISION OF DATE: {context["revision_date"]}<br/>', right_style))

    # Generate the absolute file path for the image file
    logo_path = os.path.join(settings.BASE_DIR, 'misstaffportal', 'static', 'misstaffportal', 'img', 'minsu-logo.png')

    # Create an Image object for the logo and add it to the list of elements
    logo = Image(logo_path, width=0.4*inch, height=0.4*inch)
    elements.append(logo)

    elements.append(Paragraph(context['data'], centered_style))
    elements.append(Paragraph('<br/><br/>', centered_style))

    # Create a table with three cells to hold the JID, Date of Request and Time information
    jid_year = datetime.now().year
    jid_cell = Paragraph(f'JID #: <u>{jid_year}-{appointment_id}__</u>', left_style)
    
    # Get the appointment date and time from the database
    appointment = Appointment.objects.get(id=appointment_id)
    appointment_date = appointment.appointment_date.strftime('%B %d, %Y')
    appointment_time = appointment.appointment_time.strftime('%I:%M %p')
    
    date_of_request_cell = Paragraph(f'Date of Request: <u>{appointment_date}</u>', right_style)
    time_cell = Paragraph(f'Time: <u>{appointment_time}___</u>', right_style)
    table_data = [[jid_cell, date_of_request_cell], ['', time_cell]]
    table = Table(table_data)

    # Add the table to the list of elements
    elements.append(table)

    # Add the Particulars section
    elements.append(Paragraph('<br/>Particulars:', left_style))
    
    # Get the issue description from the database
    issue_description = appointment.issue_description
    
    # Add the issue description to the list of elements
    issue_description_lines = issue_description.split('\n')
    
    table_data = []
    
    for line in issue_description_lines:
        table_data.append([Paragraph(f'{line}', left_style)])
    
    # Add extra lines depending on the length of the text
    extra_lines = 1 - len(issue_description_lines)
    
    if extra_lines > 0:
        for _ in range(extra_lines):
            table_data.append([Paragraph('', left_style)])
    
    table = Table(table_data, rowHeights=0.75*inch)
    table.setStyle([('BOX', (0, 0), (-1, -1), 0.25, 'black'), ('VALIGN', (0, 0), (-1, -1), 'TOP')])
    
    elements.append(table)
    
    # Add the Action Taken section
    elements.append(Paragraph('<br/>Action Taken:', left_style))
    
    # Get the notes from the database
    notes = appointment.notes
    
    # Add the notes to the list of elements
    notes_lines = notes.split('\n')
    
    table_data = []
    
    for line in notes_lines:
        table_data.append([Paragraph(f'{line}', left_style)])
    
    # Add extra lines depending on the length of the text
    extra_lines = 1 - len(notes_lines)
    
    if extra_lines > 0:
        for _ in range(extra_lines):
            table_data.append([Paragraph('', left_style)])
    
    table = Table(table_data, rowHeights=0.75*inch)
    table.setStyle([('BOX', (0, 0), (-1, -1), 0.25, 'black'), ('VALIGN', (0, 0), (-1, -1), 'TOP')])
    
    elements.append(table)
    
    # Add the Date of Visit section
    date_of_visit = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f'<br/>Date of Visit: {date_of_visit}', left_style))

    # Add the Status section
    status = appointment.status
    if status == 'PENDING':
        status_text = 'Status: <u>___✓___</u>Pending<u>_________</u>In Progress<u>_________</u>Completed<u>_________</u>To Follow-up'
    elif status == 'IN_PROGRESS':
        status_text = 'Status: <u>_________</u>Pending<u>___✓___</u>In Progress<u>_________</u>Completed<u>_________</u>To Follow-up'
    elif status == 'COMPLETED':
        status_text = 'Status: <u>_________</u>Pending<u>_________</u>In Progress<u>___✓___</u>Completed<u>_________</u>To Follow-up'
    elif status == 'TO_FOLLOW_UP':
        status_text = 'Status: <u>_________</u>Pending<u>_________</u>In Progress<u>_________</u>Completed<u>___✓___</u>To Follow-up'
    else:
        status_text = 'Status: <u>_________</u>Pending<u>_________</u>In Progress<u>_________</u>Completed<u>_________</u>To Follow-up'
    
    elements.append(Paragraph(f'<br/>{status_text}<br/><br/>', left_style))

    # Create a table with two cells to hold the Client/Dept. and Attending MIS Personnel information
    client_dept_cell = Paragraph('Client/Dept.:', left_style)
    attending_mis_personnel_cell = Paragraph('Attending MIS Personnel:', right_style)
    table_data = [[client_dept_cell, attending_mis_personnel_cell]]
    table = Table(table_data)

    # Add the table to the list of elements
    elements.append(table)

    # Get the full name from the appointment database
    full_name = appointment.full_name
    
    # Get the first name and last name of the logged-in user
    first_name = user.first_name
    last_name = user.last_name

    # Add the signature lines for Client/Dept. and Attending MIS Personnel
    client_dept_sig_cell = Paragraph(f'<u>_____{full_name}_____</u>', left_style)
    attending_mis_personnel_sig_cell = Paragraph(f'<u>_____{first_name} {last_name}____</u>', right_style)
    table_data = [[client_dept_sig_cell, attending_mis_personnel_sig_cell]]
    table = Table(table_data)

    # Add the table to the list of elements
    elements.append(table)

    # Add the Signature Over Printed Name text for Client/Dept. and Attending MIS Personnel
    client_dept_name_cell = Paragraph('Signature Over Printed Name', left_style)
    attending_mis_personnel_name_cell = Paragraph('Signature Over Printed Name', right_style)
    table_data = [[client_dept_name_cell, attending_mis_personnel_name_cell]]
    table = Table(table_data)

    # Add the table to the list of elements
    elements.append(table)
    
    # Add the full name and first name and last name to the list of elements

    # Build the PDF document
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=job_order_form.pdf'

    return response

@login_required
def generate_job_order_form_detail(request, appointment_id):

    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Create a new PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Job-Order-Form.pdf"'

    # Create a new canvas object that will hold the content of the PDF document
    p = canvas.Canvas(response, pagesize=letter)

    # Set the title of the PDF document
    p.setTitle("Job Order Form")


    # Set the left, right, top and bottom margin values
    left_margin = 50
    right_margin = 50
    top_margin = 0
    bottom_margin = 50

    # Generate the absolute file path for the image file
    image_path = os.path.join(settings.BASE_DIR, 'misstaffportal', 'static', 'misstaffportal', 'img', 'minsu-header.png')

    # Add the image to the canvas at the top of the page with the specified margins
    p.drawImage(image_path, left_margin, letter[1] - top_margin - 80, width=letter[0] - left_margin - right_margin, height=80)

    # Set the font to "Helvetica-Bold" with a size of 16
    p.setFont("Helvetica-Bold", 20)

    # Add the text "Job Order Form" below the image and center it
    p.drawCentredString(letter[0] / 2, letter[1] - top_margin - 80 - 30, "JOB ORDER FORM")

    # Set the font to "Helvetica" with a size of 12
    p.setFont("Helvetica", 12)

    # Get the current year
    year = datetime.now().year

    # Add the text "JOB ORDER #:" to the left side below the "JOB ORDER FORM" text
    job_order_text = f"JOB ORDER #: {year}-{appointment_id}"
    p.drawString(left_margin, letter[1] - top_margin - 80 - 60, job_order_text)

    # Calculate the width of the "JOB ORDER #:" text
    job_order_text_width = p.stringWidth(job_order_text, "Helvetica", 12)

    # Draw a line under the "{year}-{appointment_id}" text
    p.line(left_margin + 85, letter[1] - top_margin - 80 - 60 - 3, left_margin + 85 + job_order_text_width - 85, letter[1] - top_margin - 80 - 60 - 3)

    # Set the starting y position for the table
    y = letter[1] - top_margin - 80 - 60 - 30

    # Set the height of each row
    row_height = 16

    # Set the width of each column
    col_width = (letter[0] / 2 - left_margin - right_margin) / 2

    # Draw the horizontal lines of the table
    for i in range(7):
        p.line(left_margin, y - i * row_height, left_margin + col_width * 2, y - i * row_height)

    # Draw the vertical lines of the table
    p.line(left_margin, y, left_margin, y - row_height * 6)
    p.line(left_margin + col_width * 2, y, left_margin + col_width * 2, y - row_height * 6)
    p.line(left_margin + col_width, y - row_height, left_margin + col_width, y - row_height * 6)

        # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 12)

    # Add the text "TIME OF REQUEST" to the first row of the table and center it
    p.drawCentredString(left_margin + col_width, y - row_height / 2 - 6, "TIME OF REQUEST")

    # Set the font to "Helvetica" with a size of 12
    p.setFont("Helvetica", 11)

    # Add the label "Date: (mm/dd/yyyy)" to the second row of the first column
    p.drawString(left_margin + 5, y - row_height * 1.5 - 6, "Date: (mm/dd/yyyy)")

    # Get the appointment object from the database using the appointment_id
    appointment = Appointment.objects.get(id=appointment_id)

    # Get the appointment date and format it as "mm/dd/yyyy"
    appointment_date = appointment.appointment_date.strftime("%m/%d/%Y")

    # Add the value of appointment_date to the second row of the second column
    p.drawString(left_margin + col_width + 5, y - row_height * 1.5 - 6, appointment_date)

    # Add the label "Time: (hh:mm)" to the third row of the first column
    p.drawString(left_margin + 5, y - row_height * 2.5 - 6, "Time: (hh:mm)")

    # Get the appointment time and format it as "hh:mm"
    appointment_time = appointment.appointment_time.strftime("%H:%M")

    # Add the value of appointment_time to the third row of the second column
    p.drawString(left_margin + col_width + 5, y - row_height * 2.5 - 6, appointment_time)

    # Add the label "Name of Client" to the fourth row of the first column
    p.drawString(left_margin + 5, y - row_height * 3.5 - 6, "Name of Client")

    # Get the full name of the client from the appointment object
    full_name = appointment.full_name

    # Add the value of full_name to the fourth row of the second column
    p.drawString(left_margin + col_width + 5, y - row_height * 3.5 - 6, full_name)

    # Add the label "Dept/Office" to the fifth row of the first column
    p.drawString(left_margin + 5, y - row_height * 4.5 - 6, "Dept/Office")

    # Get the ServiceRequest object from the database using the appointment_id
    service_request = ServiceRequest.objects.get(appointment_id=appointment_id)

    # Get the department from the service_request object
    department = service_request.department

    # Add the value of department to the fifth row of the second column
    p.drawString(left_margin + col_width + 5, y - row_height * 4.5 - 6, department)

    # Add the label "Contact Number" to the sixth row of the first column
    p.drawString(left_margin + 5, y - row_height * 5.5 - 6, "Contact Number")

    # Get the phone number from the appointment object
    phone_number = appointment.phone_number

    # Add the value of phone_number to the sixth row of the second column
    p.drawString(left_margin + col_width + 5, y - row_height * 5.5 - 6, phone_number)

    # Set the starting x position for the new table
    x = left_margin + col_width * 2 + 20

    # Set the width of the new table
    new_table_width = col_width * 2.7

    # Set the height of the first row
    first_row_height = row_height

    # Set the height of the second row
    second_row_height = row_height * 5

    # Draw the horizontal lines of the new table
    p.line(x, y, x + new_table_width, y)
    p.line(x, y - first_row_height, x + new_table_width, y - first_row_height)
    p.line(x, y - first_row_height - second_row_height, x + new_table_width, y - first_row_height - second_row_height)

    # Draw the vertical lines of the new table
    p.line(x, y, x, y - first_row_height - second_row_height)
    p.line(x + new_table_width, y, x + new_table_width, y - first_row_height - second_row_height)

    # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 11)

    # Add the text "Brief description of what is wrong/need to be done" to the first row of the new table and center it
    p.drawCentredString(x + new_table_width / 2, y - first_row_height / 2 - 6, "Brief description of what is wrong/need to be done")

    # Set the font to "Helvetica" with a size of 11
    p.setFont("Helvetica", 11)

    # Get the issue description from the appointment object
    issue_description = appointment.issue_description

    # Add the value of issue_description to the second row of the new table
    textobject = p.beginText()
    textobject.setTextOrigin(x + 5, y - first_row_height - 10)
    textobject.textLines(issue_description)
    p.drawText(textobject)

    # Set the starting y position for the new table
    new_y = y - row_height * 6 - 20

    # Draw the horizontal lines of the new table
    for i in range(5):
        p.line(left_margin, new_y - i * row_height, left_margin + col_width * 2 + 20 + new_table_width, new_y - i * row_height)

    # Draw the vertical lines of the new table
    p.line(left_margin, new_y, left_margin, new_y - row_height * 4)
    p.line(left_margin + col_width * 2 + 20 + new_table_width, new_y, left_margin + col_width * 2 + 20 + new_table_width, new_y - row_height * 4)
    p.line(left_margin + (col_width * 2 + 20 + new_table_width) / 2, new_y - row_height, left_margin + (col_width * 2 + 20 + new_table_width) / 2, new_y - row_height * 4)

    # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 12)

    # Add the text "Type of Service Request: (Please Check)" to the first row of the new table and align it to the left
    p.drawString(left_margin + 5, new_y - row_height / 2 - 6, "Type of Service Request: (Please Check)")

    # Set the font to "Helvetica" with a size of 12
    p.setFont("Helvetica", 12)

    # Add a checkbox before each value
    checkbox = "[   ]"

    # Add a checkmark if the corresponding service type is selected in the ServiceRequest database
    if ServiceRequest.objects.filter(service_type="repair", appointment_id=appointment_id).exists():
        checkbox = "[✓]"
    p.drawString(left_margin + 5, new_y - row_height * 1.5 - 6, f"{checkbox} Repair/Troubleshoot")

    checkbox = "[   ]"
    if ServiceRequest.objects.filter(service_type="software", appointment_id=appointment_id).exists():
        checkbox = "[✓]"
    p.drawString(left_margin + 5, new_y - row_height * 2.5 - 6, f"{checkbox} Software Installation")

    checkbox = "[   ]"
    if ServiceRequest.objects.filter(service_type="formatting", appointment_id=appointment_id).exists():
        checkbox = "[✓]"
    p.drawString(left_margin + 5, new_y - row_height * 3.5 - 6, f"{checkbox} Formatting")

    # Add the values to the right three rows of the new table
    checkbox = "[   ]"
    if ServiceRequest.objects.filter(service_type="network", appointment_id=appointment_id).exists():
        checkbox = "[✓]"
    p.drawString(left_margin + (col_width * 2 + 20 + new_table_width) / 2 + 5, new_y - row_height * 1.5 - 6, f"{checkbox} Network Connectivity")

    checkbox = "[   ]"
    if ServiceRequest.objects.filter(service_type="internet", appointment_id=appointment_id).exists():
        checkbox = "[✓]"
    p.drawString(left_margin + (col_width * 2 + 20 + new_table_width) / 2 + 5, new_y - row_height * 2.5 - 6, f"{checkbox} Internet Service")

    checkbox = "[   ]"
    if ServiceRequest.objects.filter(service_type="other", appointment_id=appointment_id).exists():
        checkbox = "[✓]"
    p.drawString(left_margin + (col_width * 2 + 20 + new_table_width) / 2 + 5, new_y - row_height * 3.5 - 6, f"{checkbox} Others:")

    # Set the starting y position for the new table
    new_y = new_y - row_height * 4 - 20

    # Draw the horizontal lines of the new table
    p.line(left_margin, new_y, left_margin + col_width * 2 + 20 + new_table_width, new_y)
    p.line(left_margin, new_y - row_height, left_margin + col_width * 2 + 20 + new_table_width, new_y - row_height)

    # Draw the vertical lines of the new table
    p.line(left_margin, new_y, left_margin, new_y - row_height)
    p.line(left_margin + col_width * 2 + 20 + new_table_width, new_y, left_margin + col_width * 2 + 20 + new_table_width, new_y - row_height)

    # Set the font to "Helvetica-BoldOblique" with a size of 12
    p.setFont("Helvetica-BoldOblique", 12)

    # Add the text "To be accomplished by the attending MIS Personnel" to the first row of the new table and center it
    p.drawCentredString(left_margin + (col_width * 2 + 20 + new_table_width) / 2, new_y - row_height / 2 - 6, "To be accomplished by the attending MIS Personnel")

    # Set the starting y position for the new table
    new_table_y = new_y - row_height - 20

    # Set the width of each column in the new table
    new_table_col_width = col_width * 1.1 # Change this value to make the table wider or narrower

    # Set the height of each row in the new table
    new_table_row_height = row_height

    # Draw the horizontal lines of the new table
    for i in range(6):
        p.line(left_margin, new_table_y - i * new_table_row_height, left_margin + 2 * new_table_col_width, new_table_y - i * new_table_row_height)

    # Draw the vertical lines of the new table
    p.line(left_margin, new_table_y, left_margin, new_table_y - new_table_row_height * 5)
    p.line(left_margin + new_table_col_width, new_table_y - new_table_row_height, left_margin + new_table_col_width, new_table_y - new_table_row_height * 5)
    p.line(left_margin + 2 * new_table_col_width, new_table_y, left_margin + 2 * new_table_col_width, new_table_y - new_table_row_height * 5)

    # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 12)

    # Set the starting x position for the new table
    new_table_x = left_margin + 5

    # Add cells to the new table
    for i in range(4):
        if i == 0:
            title = "SCHEDULED RESPONSE TIME"
            title_width = stringWidth(title, "Helvetica-Bold", 12)
            cell_x = left_margin + (2 * new_table_col_width - title_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, title)
        elif i == 1:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, "Date: (mm/dd/yyyy)")
            service_request = ServiceRequest.objects.get(appointment_id=appointment_id)
            scheduled_response_date = service_request.scheduled_response_date.strftime("%m/%d/%Y")
            cell_x = new_table_x + new_table_col_width
            p.drawString(cell_x, cell_y, scheduled_response_date)
        elif i == 2:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, "Time: (hh:mm)")
            service_request = ServiceRequest.objects.get(appointment_id=appointment_id)
            scheduled_response_time = service_request.scheduled_response_time.strftime("%H:%M")
            cell_x = new_table_x + new_table_col_width
            p.drawString(cell_x, cell_y, scheduled_response_time)
        elif i == 3:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, "Verified By Client")
            service_request = ServiceRequest.objects.get(appointment_id=appointment_id)
            verified_by_client = service_request.verified_by_client
            if verified_by_client:
                cell_x = new_table_x + new_table_col_width
                p.drawString(cell_x, cell_y, "✓")
        else:
            p.setFont("Helvetica", 12)
            for j in range(2):
                cell_x = new_table_x + j * new_table_col_width
                cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
                p.drawString(cell_x, cell_y, "")

    # Set the starting x position for the new table
    new_table_x = left_margin + 2 * new_table_col_width + 20 # Change this value to adjust the horizontal spacing between the two tables

    # Set the starting y position for the new table
    new_table_y = new_y - row_height - 20

    # Set the width of each column in the new table
    new_table_col_width = col_width * 1.25 # Change this value to make the table wider or narrower

    # Set the height of each row in the new table
    new_table_row_height = row_height

    # Draw the horizontal lines of the new table
    for i in range(6): # Change this value to add more rows to the table
        p.line(new_table_x, new_table_y - i * new_table_row_height, new_table_x + 2 * new_table_col_width, new_table_y - i * new_table_row_height)

    # Draw the vertical lines of the new table
    p.line(new_table_x, new_table_y, new_table_x, new_table_y - new_table_row_height * 5) # Change this value to add more rows to the table
    p.line(new_table_x + new_table_col_width, new_table_y - new_table_row_height, new_table_x + new_table_col_width, new_table_y - new_table_row_height * 5) # Change this value to add more rows to the table
    p.line(new_table_x + 2 * new_table_col_width, new_table_y, new_table_x + 2 * new_table_col_width, new_table_y - new_table_row_height * 5) # Change this value to add more rows to the table

    # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 12)

    # Add cells to the new table
    for i in range(5): # Change this value to add more rows to the table
        if i == 0:
            title = "STATUS(Please Check)"
            title_width = stringWidth(title, "Helvetica-Bold", 12)
            cell_x = new_table_x + (2 * new_table_col_width - title_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, title)
        elif i == 1:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, " Pending")
            appointment = Appointment.objects.get(id=appointment_id)
            status = appointment.status
            if status == "PENDING":
                cell_x = new_table_x + new_table_col_width
                p.drawString(cell_x, cell_y, " ✓")
        elif i == 2:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, " In Progress")
            appointment = Appointment.objects.get(id=appointment_id)
            status = appointment.status
            if status == "IN_PROGRESS":
                cell_x = new_table_x + new_table_col_width
                p.drawString(cell_x, cell_y, " ✓")
        elif i == 3:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, " Completed")
            appointment = Appointment.objects.get(id=appointment_id)
            status = appointment.status
            if status == "COMPLETED":
                cell_x = new_table_x + new_table_col_width
                p.drawString(cell_x, cell_y, " ✓")
        elif i == 4:
            p.setFont("Helvetica", 12)
            cell_x = new_table_x
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, " To Follow-up")
            appointment = Appointment.objects.get(id=appointment_id)
            status = appointment.status
            if status == "TO_FOLLOW_UP":
                cell_x = new_table_x + new_table_col_width
                p.drawString(cell_x, cell_y, " ✓")
        else:
            p.setFont("Helvetica", 12)
            for j in range(2):
                cell_x = new_table_x + j * new_table_col_width
                cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
                p.drawString(cell_x, cell_y, "")


    # Set the starting y position for the new table
    new_table_y = new_y - row_height - 120

    # Set the width of each column in the new table
    new_table_col_width = (col_width * 2 + 20 + new_table_width) / 2

    # Set the height of each row in the new table
    new_table_row_height = row_height * 2

    # Draw the horizontal lines of the new table
    for i in range(5):
        if i == 0:
            p.line(left_margin, new_table_y - i * row_height, left_margin + col_width * 2 + 20 + new_table_width, new_table_y - i * row_height)
        else:
            p.line(left_margin, new_table_y - row_height - (i - 1) * new_table_row_height, left_margin + col_width * 2 + 20 + new_table_width, new_table_y - row_height - (i - 1) * new_table_row_height)

    # Draw the vertical lines of the new table
    p.line(left_margin, new_table_y, left_margin, new_table_y - row_height - new_table_row_height * 3)
    p.line(left_margin + col_width * 2 + 20 + new_table_width, new_table_y, left_margin + col_width * 2 + 20 + new_table_width, new_table_y - row_height - new_table_row_height * 3)
    p.line(left_margin + col_width * 1, new_table_y - row_height, left_margin + col_width * 1, new_table_y - row_height - new_table_row_height * 3) # Change this value to adjust the position of the middle vertical line

    # Set the font to "Helvetica" with a size of 12
    p.setFont("Helvetica", 12)

    # Add a label "Task Resolution" in bold in the first row
    label = "Task Resolution"
    label_width = p.stringWidth(label)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(left_margin + (col_width * 2 + 20 + new_table_width - label_width) / 2, new_table_y - row_height / 1.2, label)
    p.setFont("Helvetica", 12)

    # Add a label "Problem(s) Found" in the first column of the second row
    label = "Problem(s) Found"
    label_width = p.stringWidth(label)
    p.drawString(left_margin + (col_width - label_width) / 2, new_table_y - row_height - new_table_row_height / 2, label)

    # Add a label "Solution Applied" in the first column of the third row
    label = "Solution Applied"
    label_width = p.stringWidth(label)
    p.drawString(left_margin + (col_width - label_width) / 2, new_table_y - row_height - new_table_row_height * 1.5, label)

    # Add a label "Recommendation (If Any)" in the first column of the fourth row
    label = "Recommendation"
    label_width = p.stringWidth(label)
    p.drawString(left_margin + (col_width - label_width) / 2, new_table_y - row_height - new_table_row_height * 2.5, label)

    # Retrieve data from the Django model
    data = ServiceRequest.objects.filter(appointment_id=appointment_id).values_list('problem_found', flat=True)

    # Display the data in the table
    for i, value in enumerate(data):
        p.drawString(left_margin + col_width + 20, new_table_y - row_height - new_table_row_height / 2 - i * new_table_row_height, str(value))

    # Retrieve data from the Django model
    appointment_data = Appointment.objects.filter(id=appointment_id).values_list('notes', flat=True)

    # Display the data in the table
    for i, value in enumerate(appointment_data):
        p.drawString(left_margin + col_width + 20, new_table_y - row_height - new_table_row_height * 1.5 - i * new_table_row_height, str(value))

    # Retrieve data from the Django model
    recommendation_data = ServiceRequest.objects.filter(appointment_id=appointment_id).values_list('recommendation', flat=True)

    # Display the data in the table
    for i, value in enumerate(recommendation_data):
        p.drawString(left_margin + col_width + 20, new_table_y - row_height - new_table_row_height * 2.5 - i * new_table_row_height, str(value))

    # Set the starting y position for the new table
    new_table_y = new_y - row_height - 232

    # Set the width of each column in the new table
    new_table_col_width = col_width * 1.1 # Change this value to make the table wider or narrower

    # Set the height of each row in the new table
    new_table_row_height = row_height * 1.95

    # Draw the horizontal lines of the new table
    for i in range(4):
        if i == 2:
            p.line(left_margin, new_table_y - i * new_table_row_height - new_table_row_height / 2, left_margin + 2 * new_table_col_width, new_table_y - i * new_table_row_height - new_table_row_height / 2)
        p.line(left_margin, new_table_y - i * new_table_row_height, left_margin + 2 * new_table_col_width, new_table_y - i * new_table_row_height)

    # Draw the vertical lines of the new table
    p.line(left_margin, new_table_y, left_margin, new_table_y - new_table_row_height * 3)
    p.line(left_margin + new_table_col_width, new_table_y - new_table_row_height, left_margin + new_table_col_width, new_table_y - new_table_row_height * 3)
    p.line(left_margin + 2 * new_table_col_width, new_table_y, left_margin + 2 * new_table_col_width, new_table_y - new_table_row_height * 3)

    # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 12)

    # Set the starting x position for the new table
    new_table_x = left_margin + 5

    # Add cells to the new table
    for i in range(4):
        if i == 0:
            title = "SERVICE COMPLETED"
            title_width = stringWidth(title, "Helvetica-Bold", 12)
            cell_x = left_margin + (2 * new_table_col_width - title_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, title)
        elif i == 2:
            p.setFont("Helvetica-Bold", 11)
            label = "MIS Personnel"
            label_width = stringWidth(label, "Helvetica-Bold", 11)
            cell_x = new_table_x + (new_table_col_width - label_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 1 + 5
            p.drawString(cell_x, cell_y, label)
            
            p.setFont("Helvetica-Oblique", 8.5)
            label = "Signature over Printed Name"
            label_width = stringWidth(label, "Helvetica-Oblique", 10)
            cell_x = new_table_x + (new_table_col_width - label_width) / 4
            cell_y -= new_table_row_height / 2
            p.drawString(cell_x, cell_y, label)
            
            p.setFont("Helvetica", 8.5)
            label = "Date"
            label_width = stringWidth(label, "Helvetica-Bold", 8.5)
            cell_x = new_table_x + new_table_col_width + (new_table_col_width - label_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 1 + 5
            p.drawString(cell_x, cell_y, label)
            
            p.setFont("Helvetica", 8.5)
            label = "(mm/dd/yyyy)"
            label_width = stringWidth(label, "Helvetica", 8.5)
            cell_x = new_table_x + new_table_col_width + (new_table_col_width - label_width) / 2
            cell_y -= new_table_row_height / 2
            p.drawString(cell_x, cell_y, label)
        else:
            p.setFont("Helvetica", 12)
            for j in range(2):
                cell_x = new_table_x + j * new_table_col_width
                cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
                if i == 2:
                    cell_y -= new_table_row_height / 2
                p.drawString(cell_x, cell_y, "")

    # Set the starting x position for the new table
    new_table_x = left_margin + 2 * new_table_col_width + 51 # Change this value to adjust the horizontal spacing between the two tables

    # Draw the horizontal lines of the new table
    for i in range(4):
        if i == 2:
            p.line(new_table_x, new_table_y - i * new_table_row_height - new_table_row_height / 2, new_table_x + 2 * new_table_col_width, new_table_y - i * new_table_row_height - new_table_row_height / 2)
        p.line(new_table_x, new_table_y - i * new_table_row_height, new_table_x + 2 * new_table_col_width, new_table_y - i * new_table_row_height)

    # Draw the vertical lines of the new table
    p.line(new_table_x, new_table_y, new_table_x, new_table_y - new_table_row_height * 3)
    p.line(new_table_x + new_table_col_width, new_table_y - new_table_row_height, new_table_x + new_table_col_width, new_table_y - new_table_row_height * 3)
    p.line(new_table_x + 2 * new_table_col_width, new_table_y, new_table_x + 2 * new_table_col_width, new_table_y - new_table_row_height * 3)

    # Set the font to "Helvetica-Bold" with a size of 12
    p.setFont("Helvetica-Bold", 12)

    # Add cells to the new table
    for i in range(4):
        if i == 0:
            title = "SERVICE VERIFIED BY CLIENT"
            title_width = stringWidth(title, "Helvetica-Bold", 12)
            cell_x = new_table_x + (2 * new_table_col_width - title_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
            p.drawString(cell_x, cell_y, title)
        elif i == 2:
            p.setFont("Helvetica-Bold", 11)
            label = "Client/Dept."
            label_width = stringWidth(label, "Helvetica-Bold", 11)
            cell_x = new_table_x + (new_table_col_width - label_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 1 + 5
            p.drawString(cell_x, cell_y, label)

            p.setFont("Helvetica-Oblique", 8.5)
            label = "Signature over Printed Name"
            label_width = stringWidth(label, "Helvetica-Oblique", 10)
            cell_x = new_table_x + (new_table_col_width - label_width) / 30
            cell_y -= new_table_row_height / 2
            p.drawString(cell_x, cell_y, label)

            p.setFont("Helvetica", 8.5)
            label = "Date"
            label_width = stringWidth(label, "Helvetica-Bold", 8.5)
            cell_x = new_table_x + new_table_col_width + (new_table_col_width - label_width) / 2
            cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 1 + 5
            p.drawString(cell_x, cell_y, label)

            p.setFont("Helvetica", 8.5)
            label = "(mm/dd/yyyy)"
            label_width = stringWidth(label, "Helvetica", 8.5)
            cell_x = new_table_x + new_table_col_width + (new_table_col_width - label_width) / 2
            cell_y -= new_table_row_height / 2
            p.drawString(cell_x, cell_y, label)
        else:
            p.setFont("Helvetica", 12)
            for j in range(2):
                cell_x = new_table_x + j * new_table_col_width
                cell_y = new_table_y - i * new_table_row_height - new_table_row_height / 2 - 6
                if i == 2:
                    cell_y -= new_table_row_height / 2
                p.drawString(cell_x, cell_y, "")


    # Close the PDF object cleanly and save it to the response
    p.showPage()
    p.save()

    return response
