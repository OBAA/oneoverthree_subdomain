"""oneoverthree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView


from . import views
from account.views import GuestRegisterView, LoginView, RegisterView, StoreRegisterView
from marketing.views import MailchimpWebhookView

urlpatterns = [
    url(r'^$', views.StoreHomeView.as_view(), name='home'),
    # url(r'^about/$', about_page, name='about'),
    url(r'^contact/$', views.ContactFormView.as_view(), name='contact'),

    url(r'^register/store/$', StoreRegisterView.as_view(), name='store_register'),
    url(r'^register/guest/$', GuestRegisterView.as_view(), name='guest_register'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    # Accounts
    url(r'^accounts/login/$', RedirectView.as_view(url='/account')),
    url(r'^account/', include("accounts.urls", namespace='account')),
    url(r'^accounts/', include("accounts.passwords.urls")),

    # Addresses
    url(r'^account/address-book/', include("addresses.urls", namespace='address')),

    # Api links
    url(r'^api/', include("oneoverthree.api_urls", namespace='api')),

    # Billing related links
    url(r'^billing/', include("billing.urls", namespace='billing')),

    # Cart related links
    url(r'^cart/', include("cart.urls", namespace='cart')),

    # Marketplace related links
    url(r'^marketplace/', include("marketplace.urls", namespace='marketplace')),

    # Search related links
    url(r'^search/', include("search.urls", namespace='search')),

    # Store outlet related links
    url(r'^outlet/', include("store.urls", namespace='store')),

    # Mailchimp Webhooks
    url(r'^webhooks/mailchimp/$', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),

    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)