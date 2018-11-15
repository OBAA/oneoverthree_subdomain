from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import UpdateView, View

# from django.shortcuts import redirect
from .forms import MarketingPreferenceForm
from .mixins import CsrfExemptMixin
from .models import MarketingPreference
from .utils import Mailchimp

MAILCHIMP_API_KEY = getattr(settings, "MAILCHIMP_API_KEY", None)
MAILCHIMP_DATA_CENTER = getattr(settings, "MAILCHIMP_DATA_CENTER", None)
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)


# Create your views here.

def subscribe_to_notifications(request):
    input_email = request.POST.get("email", None)
    status_code, response_data = Mailchimp().add_email(email=input_email)
    print(response_data)

    if response_data['status'] == 'subscribed':
        return redirect("/")
    else:
        return HttpResponse("Network Error", status=200)


class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    # template_name = 'base/subscription_form.html'
    template_name = 'accounts/snippets/account-settings.html'

    # success_url = '/settings/email/'
    success_url = '/account/settings/'
    success_message = "Your subscription status has been updated successfully"

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated():
            # return HttpResponse('Not allowed', status=400)
            return redirect("/login/?next=/settings/email/")
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Notifications'
        return context

    def get_object(self, queryset=None):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user=user)
        # It returns a get_absolute url in attempt to redirect. Hence, success url.
        return obj


class MailchimpWebhookView(CsrfExemptMixin, View):
    # def get(self, request, *args, **kwargs):
    #
    #     # Accessing webhooks via GET request
    #     return HttpResponse("Thank You", status=200)


    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            hook_type = data.get('type')
            email = data.get('data[email]')
            status_code, response_data = Mailchimp().check_subscription_status(email=email)
            subscription_status = response_data['status']
            is_subbed = None
            mailchimp_subbed = None
            if subscription_status == "subscribed":
                is_subbed, mailchimp_subbed = (True, True)
            elif subscription_status == "unsubscribed":
                is_subbed, mailchimp_subbed = (False, False)

            if is_subbed is not None and mailchimp_subbed is not None:
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(
                        subscribed=is_subbed,
                        mailchimp_subscribed=mailchimp_subbed,
                        mailchimp_msg=str(data)
                    )

            return HttpResponse("Thank You", status=200)





