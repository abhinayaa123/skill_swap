
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import IssueReportForm
from .models import IssueReport
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required



@login_required
def submit_report(request):
    if request.method == 'POST':
        form = IssueReportForm(request.POST, user=request.user)

        if form.is_valid():
            reported_user = form.cleaned_data['reported_user']

            existing_report = IssueReport.objects.filter(
                reported_by=request.user,
                reported_user=reported_user
            ).exists()

            if existing_report:
                form.add_error(
                    'reported_user',
                    'You have already reported this user.'
                )
            else:
                report = form.save(commit=False)
                report.reported_by = request.user
                report.save()
                return redirect('my_reports')

    else:
        form = IssueReportForm(user=request.user)

    return render(
        request,
        'reports/submit_report.html',
        {'form': form}
    )



@login_required
def my_reports(request):
    reports = IssueReport.objects.filter(
        reported_by=request.user
    ).select_related('reported_user')

    return render(request, 'reports/my_reports.html', {'reports': reports})


@staff_member_required
def manage_reports(request):
    reports = IssueReport.objects.exclude(
        status='RESOLVED'
    ).select_related(
        'reported_by', 'reported_user'
    ).order_by('-created_at')

    return render(
        request, 
        'reports/manage_reports.html',
        {'reports': reports}
    )


@staff_member_required
def update_report_status(request, report_id):

    if request.method == 'POST':
        report = get_object_or_404(IssueReport, id=report_id)

        new_status = request.POST.get('status')

        valid_statuses = ['PENDING', 'UNDER_REVIEW', 'RESOLVED']

        if new_status in valid_statuses:
            report.status = new_status
            report.save()

        return redirect('manage_reports')

    return redirect('manage_reports')
