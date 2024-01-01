from django.shortcuts import render, redirect
from .forms import ReportEntryForm, DateFilterForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import ReportEntry
from django.forms import formset_factory
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
import csv
from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings


# Create your views here.

@login_required
def home(request):
    today = timezone.now().date()

    # Handle form submission
    if request.method == 'GET':
        form = DateFilterForm(request.GET)
        if form.is_valid():
            min_date = form.cleaned_data['min_date']
            max_date = form.cleaned_data['max_date']
            entries_today = ReportEntry.objects.filter(date_added__range=(min_date, max_date))
        else:
            entries_today = ReportEntry.objects.filter(date_added__date=today)
    else:
        entries_today = ReportEntry.objects.filter(date_added__date=today)
        form = DateFilterForm()

    return render(request, 'home.html', {'entries_today': entries_today, 'today': today, 'form': form})


@login_required
def report_entry_formset_view(request, total_formsets=15):
    ReportEntryFormSet = formset_factory(ReportEntryForm, extra=15, max_num=15)

    if request.method == 'POST':
        formset = ReportEntryFormSet(request.POST, prefix='report_entry')
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:  # Check if the form is not empty
                    form.save()
            messages.success(request, 'Form submission successful!')
            return redirect('home')
    else:
        formset = ReportEntryFormSet(prefix='report_entry')


    return render(request, 'report_formset.html', {'formset': formset})


@login_required
def generate_pdf(request):
    today = timezone.now().date()
    entries_today = ReportEntry.entries_by_day(today)
    template_path = 'pdf_template.html'
    context = {'entries_today': entries_today, 'today': today}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=report_entries_{today}.pdf'
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def generate_csv(request):
    today = timezone.now().date()
    entries_today = ReportEntry.entries_by_day(today)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=report_entries_{today}.csv'

    writer = csv.writer(response)
    writer.writerow(['Machine Number', 'Part Number', 'Part Description', 'Quantity', 'Date Added'])

    for entry in entries_today:
        writer.writerow([entry.machine_number, entry.part_number, entry.part_description, entry.quantity, entry.date_added])

    return response

@login_required
def send_file_via_email(request, file_type):
    today = timezone.now().date()
    entries_today = ReportEntry.entries_by_day(today)

    if file_type == 'pdf':
        template_path = 'pdf_template.html'
        context = {'entries_today': entries_today, 'today': today}
        template = get_template(template_path)
        html = template.render(context)
        filename = f'report_entries_{today}.pdf'

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        pisa.CreatePDF(html, dest=response)

    elif file_type == 'csv':
        filename = f'report_entries_{today}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        writer = csv.writer(response)
        writer.writerow(['Machine Number', 'Part Number', 'Part Description', 'Quantity', 'Date Added'])
        for entry in entries_today:
            writer.writerow([entry.machine_number, entry.part_number, entry.part_description, entry.quantity, entry.date_added])

    else:
        return HttpResponse('Invalid file type.')

    # Send the file via email
    subject = f'Report Entries - {today}'
    from_email = settings.EMAIL_HOST_USER  # Replace with your email
    recipient_list = ['muddyj4@gmail.com']  # Replace with the recipient's email

    email = EmailMessage(subject, '', from_email, recipient_list)
    email.attach(filename, response.getvalue(), 'application/pdf' if file_type == 'pdf' else 'text/csv')
    email.send()

    messages.success(request, f'The {file_type.upper()} file has been sent via email.')
    return redirect('home')

def logout_view(request):
    logout(request)
    return redirect('home')