from django.conf.urls import url
from . import views

app_name = 'billing'

urlpatterns = [
    url(r'^billing/payment-method/paystack/$', views.paystack_payment_method, name='pastack'),

]
