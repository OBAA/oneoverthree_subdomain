from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView
from analytics.mixins import ObjectViewedMixin
from cart.forms import CartUpdateForm
from cart.cart import Cart
from marketplace.models import Store
from tags.models import Tag

from .models import Product, ProductReview, Category  # , Brand
from .forms import SizeVariationForm


#  Create your views here.
class UpdateProductView(LoginRequiredMixin, RedirectView):
    """
    This handle POST request from the product list page.
    Saves the product_id to session.
    To prevent interrupting form POST request.
    """
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id', None)

        if product_id:
            if request.session.get("product_id"):
                del request.session['product_id']
            request.session['product_id'] = product_id

        return HttpResponseRedirect(reverse("account:dashboard:update-product"))


class ProductDetailSlugView(ObjectViewedMixin, DetailView):  # ObjectViewedMixin
    queryset = Product.objects.all()
    template_name = "store/product-detail.html"

    def get_context_data(self, *args, **kwargs):
        obj = self.get_object()
        context = super(ProductDetailSlugView, self).get_context_data(**kwargs)
        context['form'] = CartUpdateForm()
        # context['review'] = ProductReviewForm()
        context['reviews'] = ProductReview.objects.filter(product=obj)
        context['sizes'] = SizeVariationForm(obj)
        context['item'] = Cart(self.request)
        context['breadcrumbs'] = obj.store.get_ancestors(ascending=False, include_self=True)
        return context

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug2')
        try:
            instance = Product.objects.get(slug=slug, )
        except Product.DoesNotExist:
            raise Http404("Not Found")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, )
            instance = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        # object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return instance

    def yaga(self):
        p = Product.objects.all()
        for a in p:
            print(a)
            if a.base_price < 0:
                a.base_price = a.base_price
            if a.brand == '':
                a.brand = a.store.title
            a.save()


class ProductReviewFormView(RedirectView):
    def get_object(self):
        request = self.request
        product_id = request.POST.get('product_id', None)
        product = Product.objects.get_by_id(id=product_id)
        return product

    def post(self, request, *args, **kwargs):
        user = request.user
        review = request.POST.get('review', None)
        is_anonymous = request.POST.get('is_anonymous', None)
        if user.is_authenticated:
            product_review, created = ProductReview.objects.get_or_create(
                author=request.user,
                product=self.get_object(),
                content=review,
            )
            print(product_review)
            if product_review:
                if created:
                    if is_anonymous == 'True':
                        product_review.is_anonymous = True
                    product_review.save()
                    msg1 = "Review Posted successfully."
                    messages.success(request, msg1)
                else:
                    msg1 = "You already posted that."
                    messages.error(request, msg1)
            else:
                messages.error(request, "Operation failed try again later.")

        else:
            messages.error(request, "Please Sign in.")

        return HttpResponseRedirect(self.get_object().get_absolute_url())


class CategoryView(DetailView):
    template_name = "store/product-list.html"

    def get_context_data(self, **kwargs):
        paginator, products = self.get_paginated()
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['brand_list'] = Store.objects.all()
        context['category_list'] = Category.objects.all()
        context['object_list'] = products
        context['paginator'] = paginator
        context['slug'] = self.kwargs.get('slug')
        return context

    def get_queryset(self, *args, **kwargs):
        category = self.get_object()
        categories = category.get_descendants(include_self=True)  # Gets Category descendants list
        product_list = Product.objects.filter(category__in=categories).filter(
            Q(store__title='1OVER3') |
            Q(store__featured=True)
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

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        try:
            instance = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise Http404("Not Found")
        except Category.MultipleObjectsReturned:
            qs = Category.objects.filter(slug=slug)
            instance = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        return instance


class TagListView(ListView):
    template_name = "store/product-list.html"

    def get_context_data(self, *args, **kwargs):
        paginator, products = self.get_queryset()
        context = super(TagListView, self).get_context_data(**kwargs)
        context['brand_list'] = Store.objects.all()
        context['object_list'] = products
        context['paginator'] = paginator
        return context

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        page = self.request.GET.get('page', 1)
        product_list = Product.objects.filter(tags__title__contains=slug).filter(
            Q(store__title='1OVER3') |
            Q(store__featured=True)
        )
        paginator = Paginator(product_list, 2)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return paginator, products


class StoreHomeView(ListView):
    template_name = "store/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StoreHomeView, self).get_context_data(**kwargs)
        context['marketplace'] = Store.objects.all().exclude(slug='marketplace')
        context['tags'] = Tag.objects.all()
        paginator, products = self.get_paginated()
        context['object_list'] = products
        context['new_in'] = self.get_queryset().filter(new_in=True)
        context['paginator'] = paginator
        return context

    def get_queryset(self, *args, **kwargs):
        return Product.objects.all().filter(
            Q(store__title='1OVER3') |
            Q(store__featured=True)
        ).order_by('sku')

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


class UserProductHistoryView(LoginRequiredMixin, ListView):
    paginate_by = 12
    template_name = "store/user-history.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(**kwargs)
        cart_obj = Cart(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product, model_queryset=False)

        return views


