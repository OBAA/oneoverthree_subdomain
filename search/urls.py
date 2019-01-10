from django.conf.urls import url

from .views import (
    ProductSearchView, StoreSearchView
    )

urlpatterns = [
    url(r'^$', ProductSearchView.as_view(), name='query'),
    url(r'^$', StoreSearchView.as_view(), name='store-query'),
]
