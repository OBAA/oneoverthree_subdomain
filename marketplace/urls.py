from django.conf.urls import url
from . import views
from store.views import ProductDetailSlugView

app_name = 'marketplace'

urlpatterns = [
    url(r'^$', views.MarketPlaceView.as_view(), name='home'),
    url(r'^category/(?P<slug>[\w-]+)/$', views.TagListView.as_view(), name='category'),
    url(r'^(?P<slug>[\w-]+)/$', views.StoreDetailView.as_view(), name='storefront'),
    url(r'^(?P<slug1>[\w-]+)/(?P<slug2>[\w-]+)/$', ProductDetailSlugView.as_view(), name='product-detail'),
]
