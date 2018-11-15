from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views


app_name = 'addresses'

urlpatterns = [
    url(r'^$', views.AddressListView.as_view(), name='book'),
    url(r'^create/$', views.AddressCreateView.as_view(), name='create'),
    url(r'^checkout/re-use/$', views.CheckoutAddressReUseView.as_view(), name='checkout-re-use'),
    url(r'^checkout/create/$', views.CheckoutAddressCreateView.as_view(), name='checkout-create'),

    # url(r'^delete/$', csrf_exempt(views.AddressDeleteView.as_view()), name='delete'),
    # url(r'^delete/$', views.AddressDeleteView.as_view(), name='delete'),
    url(r'^delete/$', views.address_delete_view, name='delete'),
]

