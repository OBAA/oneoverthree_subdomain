from django.conf.urls import url

# from cart.views import cart_detail_api_view
from cart.api import cart_detail_api_view, checkout_complete_api_view

urlpatterns = [
    url(r'^cart/$', cart_detail_api_view, name='api-cart'),
    url(r'^checkout/complete/$', checkout_complete_api_view, name='api-cart'),
]
