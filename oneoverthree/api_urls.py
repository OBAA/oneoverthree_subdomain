from django.conf.urls import url

from . import views
from cart.views import cart_detail_api_view


urlpatterns = [
    url(r'^cart/$', cart_detail_api_view, name='api-cart'),

]
