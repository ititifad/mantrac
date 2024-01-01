from django import forms
from .models import ReportEntry

class ReportEntryForm(forms.ModelForm):
    class Meta:
        model = ReportEntry
        fields = ['machine_number', 'part_number', 'part_description', 'quantity']


class DateFilterForm(forms.Form):
    min_date = forms.DateField(label='Min Date', widget=forms.DateInput(attrs={'type': 'date'}))
    max_date = forms.DateField(label='Max Date', widget=forms.DateInput(attrs={'type': 'date'}))