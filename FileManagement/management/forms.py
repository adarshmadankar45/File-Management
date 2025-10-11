from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils.translation import gettext_lazy as _
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'mobile_number',
                 'division', 'district', 'taluka', 'village',
                 'password1', 'password2')
        labels = {
            'username': _('वापरकर्तानाव / Username'),
            'email': _('ईमेल / Email'),
            'full_name': _('पूर्ण नाव / Full Name'),
            'mobile_number': _('मोबाइल नंबर / Mobile Number'),
            'division': _('विभाग / Division'),
            'district': _('जिल्हा / District'),
            'taluka': _('तालुका / Taluka'),
            'village': _('गाव / Village'),
        }

class MasterWardForm(forms.ModelForm):
    class Meta:
        model = MasterWard
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class MasterDrawerForm(forms.ModelForm):
    class Meta:
        model = MasterDrawer
        fields = ['drawer_number', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CompartmentForm(forms.ModelForm):
    class Meta:
        model = Compartment
        fields = ['drawer', 'compartment_number', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }



class RevenueSiteForm(forms.ModelForm):
    class Meta:
        model = RevenueSite
        fields = '__all__'
        exclude = ['created_by', 'last_updated', 'registration_date', 'document_uploaded_at', 'file_no', 'locker_no']
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RevenueSiteForm, self).__init__(*args, **kwargs)
        if user and user.division:
            self.fields['division'].initial = user.division
            self.fields['division'].widget.attrs['readonly'] = True

        # Order the related objects
        self.fields['ward'].queryset = MasterWard.objects.all().order_by('ward_number')
        self.fields['drawer'].queryset = MasterDrawer.objects.all().order_by('drawer_number')
        self.fields['compartment'].queryset = Compartment.objects.all().order_by('compartment_number')

        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Make document field accept all file types
        self.fields['document_file'].widget.attrs.update({'accept': '*'})

    def clean(self):
        cleaned_data = super().clean()
        print("Form validation completed")  # Debug
        print("Cleaned data:", cleaned_data)  # Debug
        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label=_('वापरकर्तानाव / Username'),
        max_length=150
    )
    password = forms.CharField(
        label=_('पासवर्ड / Password'),
        widget=forms.PasswordInput
    )
    password_confirm = forms.CharField(
        label=_('पासवर्ड पुष्टीकरण / Confirm Password'),
        widget=forms.PasswordInput
    )
    email = forms.EmailField(
        label=_('ईमेल / Email')
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(
                _('पासवर्ड जुळत नाही / Passwords do not match')
            )