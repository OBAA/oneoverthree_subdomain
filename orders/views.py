from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView

from .models import Order, OrderItem


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_list.html'

    def get_queryset(self):
        request = self.request
        order_list = Order.objects.filter_by_billing_profile(request).paid()
        # Check if order is completed
        for order in order_list:
            order.check_order_status()
        return order_list


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.get_queryset()
        return context

    def get_object(self, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        qs = Order.objects.all().filter(order_id=order_id)
        if qs.count() == 1:
            return qs.first()

    def get_queryset(self):
        order_obj = self.get_object()
        print(order_obj)
        qs = OrderItem.objects.get_items(order_obj)
        if len(qs) > 0:
            order_items = qs
            return order_items
        return Http404


class OrderCompletedView(RedirectView):
    def post(self, request, *args, **kwargs):
        data = request.POST
        shipped_ids = data.getlist('process_ids', None)
        for shipped_id in shipped_ids:
            order_item = OrderItem.objects.get_by_id(id=shipped_id)
            order_item.status = 'completed'
            order_item.save()
        return HttpResponseRedirect(reverse("account:orders"))


