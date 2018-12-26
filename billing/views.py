from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import BillingProfile

from paystackapi.paystack import Paystack
from paystackapi.customer import Customer
from paystackapi.transaction import Transaction

#Paystack
paystack = getattr(settings, "PAYSTACK_SECRET_LIVE_KEY")
paystack_pk = getattr(settings, "PAYSTACK_PUB_TEST_KEY")


# Create your views here.
def paystack_payment_method(request):
    if request.method == "POST" and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Can not find this user"}, status_code=401)

        paystack_transaction_ref = request.POST.get('reference')
        if paystack_transaction_ref is not None:
            print(paystack_transaction_ref)
        else:
            pass

        return JsonResponse({"message": "Success! Your card was charged."})
    return HttpResponse("error", status_code=401)
