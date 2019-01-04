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
        pieces = domain.split('.')
        redirect_path = "{0}://{1}{2}".format(
                scheme, settings.DEFAULT_SITE_DOMAIN, path)

        # print(short_url)
        print(settings.DEFAULT_SITE_DOMAIN)
        print(path)
        print(redirect_path)
        print(pieces[0])
        print(domain)

        if domain == settings.DEFAULT_SITE_DOMAIN:
            return None

        else:
            store_slug = pieces[0].lower()
            new_path = "/marketplace/{0}/".format(store_slug)

            # print("--- Try block 1 ---")
            # print(new_path)
            # try:
            #     print("Try 1")
            #     match = resolve(new_path, marketplace_urls)
            #     print("tried")
            #     if match:
            #         # print(match.url_name, match.kwargs, match.namespace)
            #         return HttpResponseRedirect("{0}://{1}{2}".format(scheme, domain, new_path))
            #
            # except Resolver404:
            #     try:
            #         print("try 2")
            #         # The slashes are not being appended before getting here
            #         match = resolve(u"{0}/".format(path), marketplace_urls)
            #         if match:
            #             # print(match.url_name, match.kwargs, match.namespace)
            #             return HttpResponseRedirect("{0}://{1}{2}".format(scheme, domain, new_path))
            #     except Resolver404:
            #         print("break 1")
            #         # pass
            #         return redirect(redirect_path)

            print("--- Try block 2 ---")
            try:
                print("try 3")
                store = Store.objects.get(slug=store_slug)
                print(store)

            except Store.MultipleObjectsReturned:
                qs = Store.objects.filter(slug=store_slug)
                store = qs.first()

            except Store.DoesNotExist:
                print("break 2")
                msg = "Store not found. shop our products."
                messages.warning(request, msg)
                return redirect(redirect_path)
            if store:
                request.domain = store
                return HttpResponseRedirect("{0}://{1}{2}".format(scheme, domain, new_path))

