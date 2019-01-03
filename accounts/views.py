
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView, ListView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe

from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import GuestEmail, EmailActivation, User

from oneoverthree.mixins import NextUrlMixin, RequestFormAttachMixin
from .forms import StoreRegisterForm, StoreSliderUploadForm, StoreHeaderUploadForm
from addresses.models import Address
from billing.models import BillingProfile

# Create your views here.


class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'

    def get_object(self):
        return self.request.user


class AccountDetailsView(DetailView):
    template_name = 'accounts/snippets/account-details.html'

    def get_billing_profile(self):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        return billing_profile

    def get_object(self):
        return self.request.user


class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = qs.first()
                obj.activate()
                obj.send_activated_email()
                msg = """
                        Congratulations, Your email has been confirmed. Please login.
                                            """
                messages.success(request, msg)
                return redirect("login")
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg = """Your email has already been confirmed
                    Do you need to <a href="{link}">reset your password?</a>?    
                    """.format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    return redirect("login")
        context = {'form': self.get_form(), 'key': key}
        return render(request, 'registration/activation-error.html', context)

    def post(self, *args, **kwargs):
        # Create form to receive an email
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        request = self.request
        msg = """Activation link sent, please check your email.
        Link expires in 24hrs.
        """
        messages.success(request, mark_safe(msg))
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation_email()

        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation-error.html', context)


class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    # success_url = '/account/details/'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("account:details")


class AccountSettingsView(DetailView):
    template_name = 'accounts/snippets/account-settings.html'

    def get_object(self, queryset=None):
        return self.request.user


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    default_next = '/'
    success_url = '/'
    template_name = "accounts/login.html"

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)


class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        new_guest_email = GuestEmail.objects.create(email=email)
        self.request.session['guest_email_id'] = new_guest_email.id
        return redirect(self.get_next_url())


class StoreRegisterView(CreateView):
    form_class = StoreRegisterForm
    template_name = "marketplace/register.html"
    success_url = '/login/'

    def get_context_data(self, *args, **kwargs):
        context = super(StoreRegisterView, self).get_context_data(**kwargs)
        context['user_form'] = RegisterForm
        context['store_slider_form'] = StoreSliderUploadForm
        context['store_header_form'] = StoreHeaderUploadForm
        return context

    def form_valid(self, form):
        request = self.request

        user_form = RegisterForm(request.POST)
        store_slider_form = StoreSliderUploadForm(request.POST, request.FILES)
        store_header_form = StoreHeaderUploadForm(request.POST, request.FILES)

        user = user_form.save(commit=True)

        store = form.save(commit=False)

        # Resize product images
        if not store_slider_form.errors:
            store_slider_form.save(store=store)  # Not yet committed
        if not store_header_form.errors:
            store_header_form.save(store=store)  # Not yet committed

        store.user = user
        store.save()

        user.has_store = True

        # form.save_m2m()

        msg = "Your application has been received and is pending approval."
        messages.info(request, msg)
        return super(StoreRegisterView, self).form_valid(form)

    def form_invalid(self, form):
        request = self.request
        messages.error(request, "Operation failed try again later.")
        return super(StoreRegisterView, self).form_invalid(form)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = '/login/'




