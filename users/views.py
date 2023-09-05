import smtplib
import hashlib
import secrets
import logging
from django.shortcuts import get_object_or_404, render
from email.mime.text import MIMEText
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import VerifiedAccount
from django.contrib.auth.models import User
from .forms import SignupForm, LoginForm
from django.contrib.auth.decorators import login_required
from .forms import VerificationForm
from .forms import SignupFormAdmin
from django.contrib import messages
from .forms import AccountDetailForm
from django.contrib.auth.hashers import make_password

def send_verification_code(email, verification_code):
    message = f"Your new verification code is {verification_code}"
    msg = MIMEText(message)
    msg['Subject'] = 'New Verification Code'
    msg['From'] = '30johnpa@gmail.com'
    msg['To'] = email
    server = smtplib.SMTP('smtp.elasticemail.com', 2525)
    server.ehlo()
    server.starttls()
    server.login('30johnpa@gmail.com', '46E1C7F57A0AE6F067078B36C191050F416F')
    server.sendmail(msg['From'], [msg['To']], msg.as_string())
    server.quit()

def check_verified_account(user):
    verified_account = VerifiedAccount.objects.filter(user=user).first()
    if not verified_account or not verified_account.is_verified:
        return False
    return True

def redirect_unverified(request):
    return redirect('verification_views')

def index(request):
    return render(request, 'users/index.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Save user data to User model
            user = form.save(commit=False)
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            # Save the verification code to the VerifiedAccount model
            secret_key = 'your-secret-key'
            verification_code = secrets.token_hex(3)
            encrypted_code = hashlib.sha256((secret_key + verification_code).encode()).hexdigest()
            verified_account = VerifiedAccount.objects.create(
                user=user,
                verification_code=encrypted_code
            )

            # Send the verification code to the user's email
            send_verification_code(user.email, verification_code)

            # Authenticate and log in the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            else:
                print("Authentication failed. username={}, password={}".format(username, password))

            # Redirect to the success page
            if user is not None and user.is_authenticated:
                return redirect('verification_views')  # Change 'verification_views' to your desired URL name
            else:
                print("Authentication failed. user={}".format(user))
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})

logger = logging.getLogger(__name__)

@login_required
def verification_views(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            username = request.user.username
            verification_code = form.cleaned_data['verification_code']

            try:
                # Encrypt the input verification code
                secret_key = 'your-secret-key'
                encrypted_code = hashlib.sha256((secret_key + verification_code).encode()).hexdigest()

                # Check if there is a matching record in VerifiedAccount table
                verified_account = VerifiedAccount.objects.get(
                    user__username=username,
                    verification_code=encrypted_code,
                    is_verified=False
                )

                # Update is_verified field to True
                verified_account.is_verified = True
                verified_account.save()

                # Log success message
                logger.info(f"User {username} has been verified.")

                return redirect('login_views')

            except VerifiedAccount.DoesNotExist:
                form.add_error('verification_code', 'Invalid verification code')

                # Log failure message
                logger.warning(f"User {username} entered invalid verification code.")

    else:
        form = VerificationForm()

    return render(request, 'users/verification.html', {'form': form})

@login_required
def resend_verification_code(request):
    user = request.user
    try:
        verified_account = VerifiedAccount.objects.get(user=user)
    except VerifiedAccount.DoesNotExist:
        messages.error(request, 'No verified account found for this user.')
        return render(request, 'users/error.html')
    
    # Create a new verification code
    secret_key = 'your-secret-key'
    verification_code = secrets.token_hex(3)
    encrypted_code = hashlib.sha256((secret_key + verification_code).encode()).hexdigest()

    # Update the verified account in the database
    verified_account.verification_code = encrypted_code
    verified_account.save()

    # Send the new verification code to the user's email
    send_verification_code(user.email, verification_code)

    messages.success(request, 'New verification code has been sent to your email.')
    form = VerificationForm()
    return redirect('verification_views')

def login_views(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    # Check if the user has a verified account
                    try:
                        verified_account = VerifiedAccount.objects.get(user=user)
                        if not verified_account.is_verified:
                            messages.error(request, 'Your account is not verified yet. Please check your email for the verification code.')
                            login(request, user)
                            return redirect('verification_views')
                    except VerifiedAccount.DoesNotExist:
                        login(request, user)
                        messages.error(request, 'Your account is not verified yet. Please check your email for the verification code.')
                        return redirect('verification_views')

                    # Check if the user is staff
                    if user.is_staff:
                        login(request, user)
                        return redirect ('dashboard')
                    else:
                        login(request, user)
                        return redirect ('create_appointment')
                else:
                    messages.error(request, 'Your account is disabled')
            else:
                messages.error(request, 'Invalid login credentials')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def user_logout(request):

    logout(request)
    return redirect('index')

@login_required
def signup_view_admin(request):
    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        form = SignupFormAdmin(request.POST)
        if form.is_valid():
            # Create User instance
            user = User(
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                is_active=True,
                is_superuser=False,
                is_staff=form.cleaned_data.get('is_staff') == 'True',
            )
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            # Create VerifiedAccount instance
            secret_key = 'your-secret-key'
            verification_code = secrets.token_hex(3)
            encrypted_code = hashlib.sha256((secret_key + verification_code).encode()).hexdigest()
            verified_account = VerifiedAccount.objects.create(
                user=user,
                verification_code=encrypted_code,
                is_verified=form.cleaned_data.get('is_verified') == 'True',
            )

            return redirect('signup_view_admin')  # Change 'verification_views' to your desired URL name

    else:
        form = SignupFormAdmin()
    return render(request, 'users/signup_admin.html', {'form': form})

logger = logging.getLogger(__name__)

@login_required
def view_all_account_admin(request):
    user = request.user

    if not check_verified_account(user):
        return redirect_unverified(request)

    if not user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")
        # Fetch the required data from the User and VerifiedAccount models
    users = User.objects.all().values('id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'last_login')
    verified_accounts = VerifiedAccount.objects.all().values('user_id', 'is_verified')

    # Join the data from both models based on the user ID
    data = []
    for user in users:
        verified = next((va['is_verified'] for va in verified_accounts if va['user_id'] == user['id']), False)
        user['is_verified'] = verified
        data.append(user)

    # Render the data in a template and pass it to the context
    context = {
        'data': data
    }

    # Render the template with the data
    return render(request, 'users/view_all_account_admin.html', context)

@login_required
def view_acount_detail_admin(request, pk):
    user = get_object_or_404(User, pk=pk)
    verified_account = get_object_or_404(VerifiedAccount, user=user)
    
    if request.method == 'POST':
        form = AccountDetailForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.is_staff = form.cleaned_data['is_staff']
            user.save()
            
            verified_account.is_verified = form.cleaned_data['is_verified']
            verified_account.save()
            
            print("Account updated successfully.")
            return redirect('view_all_account_admin')
        else:
            print("Account update failed.")
    else:
        form = AccountDetailForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'users/view_acount_detail_admin.html', context)
