from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, FormView, ListView, View
from django.views.generic.edit import CreateView

from billing.models import BillingProfile
from orders.models import Order
from .models import Address
from .forms import AddressForm, CheckoutAddressForm


# Create your views here.

class AddressListView(ListView):
    template_name = 'addresses/address_home.html'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(AddressListView, self).get_context_data(**kwargs)
        context['address_default'] = Address.objects.by_billing_profile(request).filter(default=True)
        context['form'] = AddressForm
        return context

    def get_queryset(self):
        request = self.request
        address_list = Address.objects.by_billing_profile(request)
        return address_list.exclude(default=True)


class AddressCreateView(LoginRequiredMixin, CreateView):
    default_next = '/account/address-book/'
    form_class = AddressForm

    def get_success_url(self):
        return reverse("address:book")

    def form_valid(self, form):
        request = self.request

        print(form.cleaned_data)
        print(form.data)

        msg1 = "Address book full. Maximum number of addresses reached."
        msg2 = "Address successfully added."

        user = request.user
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        qs = Address.objects.by_billing_profile(request)
        if qs.count() > 3:
            messages.warning(request, msg1)
            return redirect(self.default_next)
        instance.billing_profile = billing_profile
        instance.name = user.full_name
        instance.save()
        if instance.default or not qs.exists():
            instance.set_default_address(billing_profile)
        messages.success(request, msg2)
        return super(AddressCreateView, self).form_valid(form)

    def form_invalid(self, form):
        request = self.request
        messages.error(request, "Operation failed try again later.")
        return redirect(self.default_next)


def address_delete_view(request):
    address_id = request.POST.get('address_id')
    address_obj = Address.objects.get_by_id(id=address_id)
    if address_obj:
        address_obj.delete()
        messages.success(request, "Address successfully removed.")
    else:
        messages.error(request, "Something went wrong.")
    return HttpResponseRedirect(reverse("address:book"))


class CheckoutAddressReUseView(View):
    def post(self, request):
        shipping_address_id = request.POST.get('shipping_address', None)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        order_obj, order_obj_created = Order.objects.new_or_get(request, billing_profile)
        # order_obj = Order.objects.get_by_billing_profile(request)  # if user.is_authenticated

        Order.objects.shipping_total(request, shipping_address_id, obj=order_obj)
        Order.objects.order_total(request, obj=order_obj)

        if shipping_address_id:
            if request.session.get("shipping_address_id", None):
                del request.session['shipping_address_id']
            request.session['shipping_address_id'] = shipping_address_id

            next_ = request.GET.get('next')
            next_post = request.POST.get('next')
            redirect_path = next_ or next_post or None

            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            return redirect("cart:finalize")
        return redirect("cart:home")


class CheckoutAddressCreateView(CreateView):
    default_next = '/cart/checkout/'
    form_class = CheckoutAddressForm

    def get_success_url(self):
        return reverse("cart:finalize")

    def form_valid(self, form):
        request = self.request
        shipping_address_id = request.session.get("shipping_address_id", None)
        if shipping_address_id:
            del request.session['shipping_address_id']

        msg1 = "Address book full. Maximum number of addresses reached."
        msg2 = "Address successfully added."

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        address_book_qs = Address.objects.all().filter(billing_profile=billing_profile)
        instance = form.save(commit=False)
        instance.billing_profile = billing_profile
        if instance.default:  # If instance.save from user input
            instance.set_default_address(billing_profile)
        if address_book_qs.count() > 3:
            messages.warning(request, msg1)
            return redirect(self.default_next)
        instance.save()
        shipping_address_id = instance.id
        request.session["shipping_address_id"] = shipping_address_id
        order_obj, order_obj_created = Order.objects.new_or_get(request, billing_profile)

        Order.objects.shipping_total(request, shipping_address_id, obj=order_obj)
        Order.objects.order_total(request, obj=order_obj)

        messages.success(request, msg2)
        return super(CheckoutAddressCreateView, self).form_valid(form)

    def form_invalid(self, form):
        request = self.request
        messages.error(request, "Operation failed try again later.")
        return redirect(self.default_next)
