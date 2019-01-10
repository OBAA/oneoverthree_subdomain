from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView

from .forms import ContactForm
from django.contrib import messages

from tags.models import Tag
from marketplace.models import Store
from store.models import Product


class StoreHomeView(ListView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StoreHomeView, self).get_context_data(**kwargs)
        context['marketplace'] = Store.objects.all().exclude(slug='marketplace')
        context['featured'] = self.get_queryset().filter(featured=True)
        context['platform'] = "store"
        context['tags'] = Tag.objects.all()
        return context

    def get_queryset(self, *args, **kwargs):
        return Product.objects.all()


def about_page(request):
    context = {
    }
    return render(request, "index.html", context)


class ContactFormView(FormView):
    template_name = "contact-page.html"
    form_class = ContactForm
    success_url = "/contact/"

    def form_valid(self, form):
        request = self.request

        full_name = form.cleaned_data.get("fullname")
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        content = form.cleaned_data.get("content")

        subject = subject + ' From: ' + email
        from_email = full_name + '<' + email + '>'
        message = content
        recipient_list = ['itsobaa@gmail.com', '1ov3rcollective@gmail.com']
        html_message = content

        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

        msg1 = "Your message was sent successfully."
        messages.success(request, msg1)
        return super(ContactFormView, self).form_valid(form)

    def form_invalid(self, form):
        request = self.request
        messages.error(request, "Operation failed try again later.")
        return render(self.request, 'registration/activation-error.html', context)
