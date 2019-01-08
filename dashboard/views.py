from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, RedirectView, UpdateView, TemplateView

from dashboard.models import Dashboard
from dashboard.forms import StoreHeaderUploadForm, StoreSliderUploadForm
from orders.models import OrderItem
from store.models import Product, Variation
from store.forms import (
    AddProductForm, ImageAUploadForm,
    ImageBUploadForm, ImageCUploadForm,
    ProductVariationFormSet, UpdateProductForm
)


# Create your views here.
class AddProductView(LoginRequiredMixin, CreateView):
    form_class = AddProductForm
    model = Product
    template_name = "dashboard/add-product.html"
    success_url = '/account/dashboard/'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(AddProductView, self).get_context_data(**kwargs)
        context['add_product'] = AddProductForm()
        context['image_a'] = ImageAUploadForm()
        context['image_b'] = ImageBUploadForm()
        context['image_c'] = ImageCUploadForm()
        context['variations'] = ProductVariationFormSet()
        return context

    def form_valid(self, form):
        request = self.request
        image_a_form = ImageAUploadForm(request.POST, request.FILES)
        image_b_form = ImageBUploadForm(request.POST, request.FILES)
        image_c_form = ImageCUploadForm(request.POST, request.FILES)
        variation_formset = ProductVariationFormSet(request.POST, request.FILES)

        # Create product object
        product = form.save(commit=False)

        # Resize product images
        if not image_a_form.errors:
            image_a_form.save(product=product)
        if not image_b_form.errors:
            image_b_form.save(product=product)
        if not image_c_form.errors:
            image_c_form.save(product=product)

        product.save()
        form.save_m2m()

        # Check Variation Form
        for variation_form in variation_formset:
            if variation_form.is_valid() and variation_form.cleaned_data != {}:
                variation = variation_form.save(product=product, commit=False)

                # Save product instance
                if variation:
                    variation.save()
                    product.has_variants = True

        # Update product stock
        if product.has_variants:
            stock = 0
            qs = Variation.objects.all().filter(product=product)
            for variation in qs:
                stock = stock + variation.quantity
            product.new_in = True
            product.stock = stock
        product.save()

        msg = "Product Added to STORE successfully"
        messages.success(request, msg)
        return super(AddProductView, self).form_valid(form)

    def form_invalid(self, form):
        request = self.request
        messages.error(request, "Operation failed try again later.")
        return super(AddProductView, self).form_invalid(form)


class UpdateProductFormView(LoginRequiredMixin, UpdateView):
    form_class = UpdateProductForm
    template_name = "dashboard/update-product.html"
    success_url = '/account/dashboard/product-list/'

    def get_object(self, queryset=None):
        request = self.request
        product_id = request.session.get('product_id', None)
        product = Product.objects.get_by_id(id=product_id)
        return product

    def get_context_data(self, *args, **kwargs):
        variation_data = self.get_initial_variation()
        context = super(UpdateProductFormView, self).get_context_data(**kwargs)
        context['image_a'] = ImageAUploadForm()
        context['image_b'] = ImageBUploadForm()
        context['image_c'] = ImageCUploadForm()
        context['variations'] = ProductVariationFormSet(initial=variation_data)
        return context

    def get_initial(self):
        p = self.get_object()
        initial = super(UpdateProductFormView, self).get_initial()

        for field, _cls in self.form_class.base_fields.items():
            # print(field, _cls)

            value = getattr(self.get_object(), field)
            if field == 'tags':
                value = self.get_object().tags.all()
            # print(field, '-', value)
            initial.update({field: value})
        return initial

    def get_initial_variation(self):
        product = self.get_object()
        qs = Variation.objects.all().filter(product=product)
        data = [{
            'size': variation.size,
            'quantity': variation.quantity,
        }for variation in qs]
        return data

    def form_valid(self, form):
        msg = None
        request = self.request
        image_a_form = ImageAUploadForm(request.POST, request.FILES)
        image_b_form = ImageBUploadForm(request.POST, request.FILES)
        image_c_form = ImageCUploadForm(request.POST, request.FILES)
        variation_formset = ProductVariationFormSet(
            data=request.POST,
            files=request.FILES, initial=self.get_initial_variation())

        # Create product object
        product = form.save(commit=False)
        print(product)

        # Resize product images
        if not image_a_form.errors:
            image_a_form.save(product=product)
        if not image_b_form.errors:
            image_b_form.save(product=product)
        if not image_c_form.errors:
            image_c_form.save(product=product)

        # Check Variation Form
        initial_data = self.get_initial_variation()
        product_variation_qs = Variation.objects.all().filter(product=product)
        if variation_formset.is_valid():
            cleaned_variation_formset = [v for v in variation_formset.cleaned_data if v != {}]
            # print(cleaned_variation_formset)
            # print(initial_data)

            """ 
            If initial data and cleaned variation data don't match,
            DELETE all variation data.             
            """
            if initial_data != cleaned_variation_formset:  # Variation has changed
                # print("variation form changed")
                for variation in product_variation_qs:
                    variation.delete()
                    # print("deleted")

                e_msg = None
                for variation_form in variation_formset:
                    if variation_form.cleaned_data != {}:
                        product.has_variants = True
                        new_variation = variation_form.save(product=product, commit=False)

                        # Save product instance
                        if new_variation.quantity == 0:
                            pass
                        elif new_variation:
                            try:
                                new_variation.save()
                            except IntegrityError:
                                e_msg = "Multiple instances of same SIZE. Additional entry IGNORED"
                                pass
                            msg = "Product updated successfully."

                # Update product stock
                stock = 0
                qs = Variation.objects.all().filter(product=product)
                for variation in qs:
                    stock = stock + variation.quantity
                product.stock = stock
                print(product.stock)

                # Size INTEGRITY ERROR message as e_msg.
                if e_msg:
                    return self.form_invalid(form, e_msg=e_msg)

            else:
                print("3")
                msg = "Product not updated. Nothing was changed."

        # Save product instance
        # if product.discount > 0 or product.discount is not None:
        if product.discount is not None:
            if product.discount > 0:
                product.on_sale = True
            else:
                product.on_sale = False
        product.save()
        form.save_m2m()
        if form.has_changed():
            print(form.has_changed())
            msg = "Product updated successfully."

        messages.success(request, msg)
        return super(UpdateProductFormView, self).form_valid(form)

    def form_invalid(self, form, e_msg=None):
        request = self.request
        msg = "Operation failed try again later."
        if e_msg:
            msg = e_msg
        messages.error(request, msg)
        return super(UpdateProductFormView, self).form_invalid(form)


class DeleteProductView(LoginRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product_obj = Product.objects.get_by_id(id=product_id)
        if product_obj:
            product_obj.delete()
            messages.success(request, "Product successfully deleted.")
        else:
            messages.error(request, "Something went wrong.")
        return HttpResponseRedirect(reverse("account:dashboard:products"))


class DashboardProductListView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/product_list.html'

    def get_context_data(self, *args, **kwargs):
        paginator, products = self.get_paginated()
        context = super(DashboardProductListView, self).get_context_data(**kwargs)
        context['products'] = products
        context['paginator'] = paginator
        context['image_a'] = ImageAUploadForm()
        context['image_b'] = ImageBUploadForm()
        context['image_c'] = ImageCUploadForm()
        context['variations'] = ProductVariationFormSet()
        return context

    def get_paginated(self):
        page = self.request.GET.get('page', 1)
        store = self.get_object()
        product_list = Product.objects.all().filter(store=store).order_by('-timestamp')
        products_per_page = 10
        paginator = Paginator(product_list, products_per_page)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return paginator, products

    def get_object(self, *args, **kwargs):
        user = self.request.user
        # return user.store
        try:
            store = user.store
        except ObjectDoesNotExist:
            raise Http404("Access restricted to authorized users ONLY.")
        except Dashboard.MultipleObjectsReturned:
            qs = Dashboard.objects.filter(user=user)
            store = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        if store:
            Dashboard.objects.all_time_sales(store)
            return store


class DashboardOrdersView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/order_list.html'

    def get_context_data(self, *args, **kwargs):
        store = self.get_object()
        context = super(DashboardOrdersView, self).get_context_data(**kwargs)
        context['pending_orders'] = Dashboard.objects.pending_orders(store)
        context['processing_orders'] = Dashboard.objects.processing_orders(store)
        context['completed_orders'] = Dashboard.objects.completed_orders(store)
        return context

    def get_object(self, *args, **kwargs):
        user = self.request.user
        # return user.store
        try:
            store = user.store
        except ObjectDoesNotExist:
            raise Http404("Access restricted to authorized users ONLY.")
        except Dashboard.MultipleObjectsReturned:
            qs = Dashboard.objects.filter(user=user)
            store = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        if store:
            Dashboard.objects.all_time_sales(store)
            return store


class DashboardHomeView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, *args, **kwargs):
        store = self.get_object()
        context = super(DashboardHomeView, self).get_context_data(**kwargs)
        context['store_slider_form'] = StoreSliderUploadForm()
        context['store_header_form'] = StoreHeaderUploadForm()
        context['store'] = store
        context['dashboard'] = Dashboard.objects.get_dashboard(store)
        return context

    def get_object(self, *args, **kwargs):
        user = self.request.user
        # return user.store
        try:
            store = user.store
        except ObjectDoesNotExist:
            raise Http404("Access restricted to authorized users ONLY.")
        except Dashboard.MultipleObjectsReturned:
            qs = Dashboard.objects.filter(user=user)
            store = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        if store:
            Dashboard.objects.all_time_sales(store)
            return store


class StoreImageUploadView(LoginRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        store = self.get_object()
        store_slider_form = StoreSliderUploadForm(request.POST, request.FILES)
        store_header_form = StoreHeaderUploadForm(request.POST, request.FILES)

        msg = msg1 = msg2 = None

        # Resize product images
        if not store_slider_form.errors:
            store.slider_image = request.FILES.get('slider_image')
            store_slider_form.save(store=store)  # Not yet committed
            msg1 = "Store slider image updated successfully."
            msg = msg1
        if not store_header_form.errors:
            store.header_image = request.FILES.get('header_image')
            store_header_form.save(store=store)  # Not yet committed
            msg2 = "Store header image updated successfully."
            msg = msg2
        store.save()

        if msg1 and msg2:
            msg = "Store updated successfully."
        messages.success(request, msg)

        return HttpResponseRedirect(reverse("account:dashboard:home"))

    def get_object(self, *args, **kwargs):
        user = self.request.user
        # return user.store
        try:
            store = user.store
        except ObjectDoesNotExist:
            raise Http404("Access restricted to authorized users ONLY.")
        except Dashboard.MultipleObjectsReturned:
            qs = Dashboard.objects.filter(user=user)
            store = qs.first()
        except:
            raise Http404("Nothing Here. Sorry")
        if store:
            Dashboard.objects.all_time_sales(store)
            return store


class OrderProcessingView(RedirectView):
    def post(self, request, *args, **kwargs):
        data = request.POST
        pending_ids = data.getlist('process_ids', None)
        for pending_id in pending_ids:
            order_item = OrderItem.objects.get_by_id(id=pending_id)
            order_item.status = 'processing'
            order_item.save()
        return HttpResponseRedirect(reverse("account:dashboard:orders"))


class OrderShippedView(RedirectView):
    def post(self, request, *args, **kwargs):
        data = request.POST
        shipped_ids = data.getlist('process_ids', None)
        # customers = []
        for shipped_id in shipped_ids:
            order_item = OrderItem.objects.get_by_id(id=shipped_id)
            order_item.status = 'shipped'
            order_item.save()
        #     customers.append(order_item.order.billing_profile.user)
        #
        #     customer = order_item.order.billing_profile.user
        #     customers.append({customer: order_item.product})
        #
        # customers = list(set(customers))
        # for customer in customers:
        #     context = {
        #         'first_name': customer.first_name
        #     }
        #     txt_ = get_template("registration/emails/verify.txt").render(context)
        #     html_ = get_template("registration/emails/verify.html").render(context)
        #     subject = 'Order Shipped'
        #     from_email = settings.DEFAULT_FROM_EMAIL
        #     recipient_list = [customer.email]
        #     sent_mail = send_mail(
        #         subject,
        #         txt_,
        #         from_email,
        #         recipient_list,
        #         html_message=html_,
        #         fail_silently=False,
        #     )
        #     return sent_mail

        return HttpResponseRedirect(reverse("account:dashboard:orders"))

