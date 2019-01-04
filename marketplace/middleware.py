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
        domain = request.META['HOST']
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
        try:
            print("Tried")
            resolve(path, marketplace_urls)
        except Resolver404:
            try:
                # The slashes are not being appended before getting here
                resolve(u"{0}/".format(path), marketplace_urls)
            except Resolver404:
                return redirect(redirect_path)
        try:
            store = Store.objects.get(title=pieces[0])
            # if short_url:
            #     store = Store.objects.get(title=short_url)
            # else:
            #     store = Store.objects.get(title=pieces[0])
        except Store.DoesNotExist:
            return redirect(redirect_path)

        request.domain = store
        store_home = "/marketplace/{0}/".format(store.slug)
        return HttpResponseRedirect("{0}://{1}{2}".format(scheme, domain, store_home))

