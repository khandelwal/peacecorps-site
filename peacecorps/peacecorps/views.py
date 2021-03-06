from uuid import uuid4
from datetime import datetime

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest

from peacecorps.forms import DonationPaymentForm


def humanize_amount(amount_cents):
    """ Return a string that presents the donation amount in a humanized
    format. """

    amount_dollars = amount_cents/100.0
    return "$%.2f" % (amount_dollars)

from peacecorps.models import FeaturedIssue, FeaturedProjectFrontPage, Issue
from peacecorps.models import Project


def donation_payment_individual(request):
    """ This is the view for the donations contact information form. """


def donation_payment(request):
    """ Collect donor contact information. """


    amount = request.GET.get('amount', None)
    project_code = request.GET.get('project', None)

    if amount is None or project_code is None:
        return HttpResponseBadRequest(
            'amount and project_code must be provided.')
    try:
        amount = int(amount)
    except ValueError:
        return HttpResponseBadRequest('amount must be an integer value')

    readable_amount = humanize_amount(amount)

    if request.method == 'POST':
        form = DonationPaymentForm(request.POST)

        if form.is_valid():
            for k, v in form.cleaned_data.items():
                #   @todo - need to remove the reliance on sessions
                request.session[k] = v
            return HttpResponseRedirect('/donations/review')
    else:
        data = {'donation_amount': amount, 'project_code': project_code}
        form = DonationPaymentForm(initial=data)

    return render(
        request, 'donations/donation_payment.jinja',
        {
            'form': form,
            'amount': readable_amount,
            'project_code': project_code
        })


def generate_agency_tracking_id():
    """ Generate an agency tracking ID for the transaction that has some random
    component. I include the date in here too, in case that's useful. (The
    current non-random tracking id has the date in it. """

    random = str(uuid4()).replace('-', '')
    today = datetime.now().strftime("%m%d")
    return 'PCOCI%s%s' % (today, random[0:6])


def generate_agency_memo(data):
    """Build the memo field from selections on the form"""
    memo = ''
    memo += '(' + data.get('comments', '').strip() + ')'
    memo += '(' + data.get('phone_number', '').strip() + ')'

    amount = humanize_amount(data['donation_amount'])
    memo += '(%s, %s)' % (data['project_code'], amount)

    if data.get('information_consent', '') == 'vol-consent-yes':
        memo += '(yes)'
    else:
        memo += '(no)'

    if data.get('interest_conflict'):
        memo += '(yes)'
    else:
        memo += '(no)'

    if data.get('email_consent'):
        memo += '(yes)'
    else:
        memo += '(no)'

    return memo


def generate_custom_fields(data):
    """Return a dictionary composed of 'custom' fields, formatted the way we
    expect."""
    custom = {}
    custom['custom_field_1'] = '(' + data.get('phone_number', '') + ')'
    custom['custom_field_1'] += '(' + data.get('email', '') + ')'
    custom['custom_field_2'] = '(' + data.get('street_address', '') + ')'

    custom['custom_field_3'] = '(' + data.get('city', '') + ')'
    custom['custom_field_3'] += '(' + data.get('state', '') + ')'
    custom['custom_field_3'] += '(' + data.get('zip_code', '') + ')'
    custom['custom_field_4'] = '(' + data.get('organization_name', '') + ')'

    custom['custom_field_5'] = '(' + data.get('dedication_name', '') + ')'
    custom['custom_field_5'] += '(' + data.get('dedication_contact', '') + ')'
    custom['custom_field_5'] += '(' + data.get('dedication_email', '') + ')'

    if data.get('dedication_type') == 'in-memory':
        custom['custom_field_6'] = '(Memory)'
    else:
        custom['custom_field_6'] = '(Honor)'
    if data.get('dedication_consent') == 'no-dedication-consent':
        custom['custom_field_6'] += '(no)'
    else:
        custom['custom_field_6'] += '(yes)'
    custom['custom_field_6'] += '(' + data.get('card_dedication', '') + ')'
    custom['custom_field_7'] = '(' + data.get('dedication_address', '') + ')'
    return custom


def donation_payment_review(request):
    """ This view is for a simple donation payment review page. """
    data = {}
    for k, v in request.session.items():
        data[k] = v

    #   We'd save the custom fields somewhere here. Right now we'll just
    #   generate and throw away
    generate_custom_fields(data)

    return render(
        request,
        'donations/review_payment.jinja',
        {
            'data': data,
            'agency_memo': generate_agency_memo(data),
            'agency_id': settings.PAY_GOV_AGENCY_ID,
            'tracking_id': generate_agency_tracking_id(),
            'app_name': settings.PAY_GOV_APP_NAME,
            'oci_servlet_url': settings.PAY_GOV_OCI_URL,
        })


def donate_landing(request):

    featuredprojects = [x.project for x in FeaturedProjectFrontPage.objects.all()]
    try:
        featuredissue = FeaturedIssue.objects.get(id=1).issue
    except FeaturedIssue.DoesNotExist:
        featuredissue = None

    return render(
        request,
        'donations/donate_landing.jinja',
        {
            'featuredissue': featuredissue,
            'issues': Issue.objects.all(),
            'featuredprojects': featuredprojects,
            'projects': Project.objects.all(),
        })

def donate_issue(request, slug):

    issue = Issue.objects.get(slug=slug)
    featured = Project.objects.filter(issue=issue, issue_feature=True)
    projects = Project.objects.filter(issue=issue)

    return render(
        request,
        'donations/donate_issue.jinja',
        {
            'issue': issue,
            'featured': featured,
            'projects': projects,
        })

def donate_project(request, slug):

    project = Project.objects.get(slug=slug)
    # Passing this in separately to prevent multiple DB queries.
    volunteer = project.volunteer

    return render(
        request,
        'donations/donate_project.jinja',
        {
            'project': project,
            'volunteer': volunteer,
        })



