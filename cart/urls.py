from django.conf.urls import url
from . import views

app_name = 'cart'

urlpatterns = [
    url(r'^$', views.cart_home, name='home'),
    url(r'^add/$', views.add_to_cart, name='add-list'),
    url(r'^update/$', views.UpdateCartView.as_view(), name='update'),  # Product Detail View
    url(r'^update-cart/$', views.cart_update_view, name='update-cart'),  # Update cart form
    url(r'^remove/$', views.cart_remove, name='remove'),
    url(r'^checkout/$', views.checkout_home, name='checkout'),
    url(r'^checkout/coupon/$', views.use_coupon_code, name='coupon'),
    url(r'^checkout/finalize/$', views.checkout_finalize, name='finalize'),
    url(r'^checkout/success/$', views.checkout_success, name='success'),
    url(r'^checkout/invoice/$', views.show_order_invoice, name='invoice'),
]
