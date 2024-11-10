"""forms.py"""

import calendar
from datetime import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Project, ProjectBudget, EmployeeResource
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user with role selection."""
    usable_password = None
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Project.objects.filter(name=name).exists():
            raise forms.ValidationError('A project with this name already exists. Please choose a different name.')
        return name
    
class ProjectBudgetForm(forms.ModelForm):
    """Form for specifying budget details."""

    month_choices = [(month, month) for month in calendar.month_abbr[1:]]
    year_choices = [(str(year), str(year)) for year in range(datetime.now().year, datetime.now().year + 5)]

    month = forms.ChoiceField(
        choices=month_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.ChoiceField(
        choices=year_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ProjectBudget
        fields = ['month', 'year', 'budgeted_resources']
        widgets = {
            'budgeted_resources': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.10', 'max': '10.00'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectBudgetForm, self).__init__(*args, **kwargs)

        current_month = calendar.month_abbr[datetime.now().month]
        current_year = str(datetime.now().year)

        self.fields['month'].initial = current_month
        self.fields['year'].initial = current_year

class EmployeeForm(forms.ModelForm):
    """Form for Employee"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label='Email Address'
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='First Name'
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Last Name'
    )

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An employee with this email already exists.")
        return email

class EmployeeResourceForm(forms.ModelForm):
    """Form for Employee Resource"""
    class Meta:
        model = EmployeeResource
        fields = ['employee', 'allocation_ratio']

    allocation_ratio = forms.CharField(
        max_length=10,
        help_text="Enter a number between 0.10 and 1.00, or type 'intern'.",
        required=True
    )

    def clean_allocation_ratio(self):
        allocation_ratio = self.cleaned_data.get('allocation_ratio').strip().lower()

        if allocation_ratio == 'intern':
            return allocation_ratio

        try:
            allocation_ratio = float(allocation_ratio)
        except ValueError:
            raise forms.ValidationError("Please enter a valid number between 0.10 and 1.00, or the word 'intern'.")

        if not (0.10 <= allocation_ratio <= 1.00):
            raise forms.ValidationError("Allocation ratio must be between 0.10 and 1.00.")

        return round(allocation_ratio, 2)
