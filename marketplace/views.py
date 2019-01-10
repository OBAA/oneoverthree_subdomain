from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, TemplateView

from store.models import Product
from tags.models import Tag

from .models import Store


# Create your views here.
class TagListView(ListView):
    template_name = "store/product-list.html"

    def get_context_data(self, *args, **kwargs):
        paginator, products = self.get_paginated()
        context = super(TagListView, self).get_context_data(**kwargs)
        context['brand_list'] = Store.objects.brands().exclude(slug='1over3')
        context['object_list'] = products
        context['paginator'] = paginator
        context['platform'] = "The Marketplace"
        context['slug'] = self.kwargs.get('slug')
        return context

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        product_list = Product.objects.all().filter(tags__slug__contains=slug).exclude(
            store__slug='1over3'
        )
        return product_list

    def get_paginated(self):
        page = self.request.GET.get('page', 1)
        product_list = self.get_queryset()
        products_per_page = 12
        paginator = Paginator(product_list, products_per_page)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return paginator, products


class StoreDetailView(DetailView):
    template_name = "marketplace/store-detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StoreDetailView, self).get_context_data(**kwargs)
        paginator, products = self.get_paginated()
        context['brand_list'] = Store.objects.all().exclude(slug='1over3')
        context['object_list'] = products
        context['paginator'] = paginator
        context['new_in'] = self.get_queryset().filter(new_in=True)
        return context

    def get_queryset(self, *args, **kwargs):
        store = self.get_object()
        Product.objects.check_new_in(store)  # Check New In Lifespan
        marketplace = store.get_descendants(include_self=True)  # Gets Brand descendants list
        product_list = Product.objects.all().filter(store__in=marketplace)
        return product_list

    def get_paginated(self):
        page = self.request.GET.get('page', 1)
        product_list = self.get_queryset()
        products_per_page = 12
        paginator = Paginator(product_list, products_per_page)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return paginator, products

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        return Store.objects.get_by_slug(slug)


class MarketPlaceView(TemplateView):
    template_name = "marketplace/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MarketPlaceView, self).get_context_data(**kwargs)
        context['marketplace'] = Store.objects.all().exclude(slug='1over3')
        context['platform'] = "marketplace"
        context['tags'] = Tag.objects.all()
        return context


