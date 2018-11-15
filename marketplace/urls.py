from django.conf.urls import url
from . import views

app_name = 'marketplace'

urlpatterns = [
    url(r'^$', views.MarketPlaceView.as_view(), name='home'),
    url(r'^category/(?P<slug>[\w-]+)/$', views.TagListView.as_view(), name='category'),
    url(r'^(?P<slug>[\w-]+)/$', views.StoreDetailView.as_view(), name='storefront'),
]
