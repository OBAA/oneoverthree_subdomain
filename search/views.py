from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from store.models import Product


# Create your views here.
class ProductSearchView(ListView):
    paginate_by = 10
    template_name = "search/search-view.html"

    def get_context_data(self, *args, **kwargs):
        query = self.request.GET.get('q')
        context = super(ProductSearchView, self).get_context_data(**kwargs)
        context['query'] = query
        context['featured_list'] = Product.objects.featured()
        return context

    def get_queryset(self, *args, **kwargs):
        method_dict = self.request.GET
        query = method_dict.get('q', None)
        if query is not None:
            return Product.objects.search_site(query)
        return Product.objects.featured()


class StoreSearchView(ListView):
    paginate_by = 10
    template_name = "search/search-view.html"

    def get_context_data(self, *args, **kwargs):
        query = self.request.GET.get('q')
        context = super(StoreSearchView, self).get_context_data(**kwargs)
        context['query'] = query
        context['featured'] = Product.objects.featured()
        return context

    def get_queryset(self, *args, **kwargs):
        store_slug = self.request.GET.get("store_slug", None)
        method_dict = self.request.GET
        query = method_dict.get('q', None)
        if query is not None:
            return Product.objects.search_store(query, store_slug)
        return Product.objects.featured()

