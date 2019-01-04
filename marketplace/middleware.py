from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect

from oneoverthree import urls as marketplace_urls
from marketplace.models import Store



try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class StoreSubdomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        scheme = "http" if not request.is_secure() else "https"
        path = request.get_full_path()
        domain = request.META['HTTP_HOST']
        # short_url = request.META.get("HTTP_X_CUSTOMURL")
        pieces = domain.split('.')
        redirect_path = "http://{0}{1}".format(
                settings.DEFAULT_SITE_DOMAIN, path)

        # print(short_url)
        print(settings.DEFAULT_SITE_DOMAIN)
        print(path)
        print(redirect_path)
        print(pieces[0])
        print(domain)

        if domain == settings.DEFAULT_SITE_DOMAIN:
            return None

        # try:
        #     print("Tried")
        #     resolve(path, marketplace_urls)
        #     print("try 1")
        # except Resolver404:
        #     try:
        #         # The slashes are not being appended before getting here
        #         resolve(u"{0}/".format(path), marketplace_urls)
        #         print("try 2")
        #     except Resolver404:
        #         print("break 1")
        #         return redirect(redirect_path)

        new_path = "/marketplace/{0}/".format(pieces[0])

        print("--- 2nd Try block ---")
        print(new_path)
        try:
            print("Try 1")
            resolve(new_path, marketplace_urls)
            print("tried")
        except Resolver404:
            try:
                print("try 2")
                # The slashes are not being appended before getting here
                resolve(u"{0}/".format(path), marketplace_urls)
            except Resolver404:
                print("break 1")
                pass
                # return redirect(redirect_path)

        print("--- 2nd Try block ---")
        try:
            print("try 3")
            store = Store.objects.get(title=pieces[0])
            print(store)
            # if short_url:
            #     store = Store.objects.get(title=short_url)
            # else:
            #     store = Store.objects.get(title=pieces[0])
        except Store.DoesNotExist:
            print("break 2")
            msg = "Store not found. shop our products."
            messages.success(request, msg)
            return redirect(redirect_path)

        request.domain = store
        store_home = "/marketplace/{0}/".format(store.slug)
        return HttpResponseRedirect("{0}://{1}{2}".format(scheme, domain, store_home))

