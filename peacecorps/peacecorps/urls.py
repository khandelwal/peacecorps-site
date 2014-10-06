from django.conf.urls import patterns, include, url
from django.contrib import admin

from peacecorps.views import donation_payment_individual
from peacecorps.views import donation_payment_organization
from peacecorps.views import donation_payment_review

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^donations/contribute/individual$',
        donation_payment_individual, name='donations_individual'),
    url(
        r'^donations/contribute/organization$',
        donation_payment_organization, name='donations_organization'),
    url(
        r'^donations/review$',
        donation_payment_review, name='donations_review'),
)