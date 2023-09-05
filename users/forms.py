from django import forms
from django.core.validators import validate_email, RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import User, VerifiedAccount
from django.contrib.auth import authenticate, login

class SignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'First name',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Last name',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Username',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }), validators=[RegexValidator(r'^[\w-]+$', message='Username can only contain alphanumeric characters, underscores and hyphens.')])
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Email',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }), validators=[validate_email])
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Password',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages = {'unique': 'Username is already taken.'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address is already in use.')
        return email
    
class VerificationForm(forms.Form):
    verification_code = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Verification Code',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class SignupFormAdmin(forms.Form):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'First name',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Last name',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Username',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }), validators=[RegexValidator(r'^[\w-]+$', message='Username can only contain alphanumeric characters, underscores and hyphens.')])
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Email',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }), validators=[validate_email])
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Password',
        'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
    }))
    is_staff = forms.ChoiceField(choices=[(False, 'No'), (True, 'Yes')], widget=forms.Select(attrs={
        'class': 'form-select mb-3',
        'id': 'is_staff_select'
    }))
    is_verified = forms.ChoiceField(choices=[(False, 'No'), (True, 'Yes')], widget=forms.Select(attrs={
        'class': 'form-select mb-3',
        'id': 'is_verified_select'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages = {'unique': 'Username is already taken.'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address is already in use.')
        return email

class AccountDetailForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'First name',
            'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Last name',
            'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
        })
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Username',
            'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
        }),
        validators=[RegexValidator(r'^[\w-]+$', message='Username can only contain alphanumeric characters, underscores, and hyphens.')]
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Email',
            'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
        }),
        validators=[validate_email]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Password',
            'onchange': "this.className=(this.value.length)?'form-control mb-3 is-valid':'form-control mb-3'"
        })
    )
    is_staff = forms.ChoiceField(
        choices=[(False, 'No'), (True, 'Yes')],
        widget=forms.Select(attrs={
            'class': 'form-select mb-3',
            'id': 'is_staff_select'
        })
    )
    is_verified = forms.ChoiceField(
        choices=[(False, 'No'), (True, 'Yes')],
        widget=forms.Select(attrs={
            'class': 'form-select mb-3',
            'id': 'is_verified_select'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages = {'unique': 'Username is already taken.'}
        
        if self.instance:
            verified_account = VerifiedAccount.objects.filter(user=self.instance).first()
            if verified_account:
                self.fields['is_verified'].initial = verified_account.is_verified
            self.fields['is_staff'].initial = self.instance.is_staff