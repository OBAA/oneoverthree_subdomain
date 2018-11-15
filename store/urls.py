from django.conf.urls import url

from . import views

app_name = 'store'

urlpatterns = [
    url(r'^$', views.StoreHomeView.as_view(), name='home'),
    url(r'^update-product/$', views.UpdateProductView.as_view(), name='update-product'),
    url(r'^product-review/$', views.ProductReviewFormView.as_view(), name='product-review'),
    url(r'^(?P<slug>[\w-]+)/$', views.CategoryView.as_view(), name='categories'),
    # url(r'^category/(?P<slug>[\w-]+)/$', views.TagListView.as_view(), name='tags'),
    # url(r'^brand/(?P<slug>[\w-]+)/$', views.BrandDetailSlugView.as_view(), name='brands'),
    url(r'^(?P<slug1>[\w-]+)/(?P<slug2>[\w-]+)/$', views.ProductDetailSlugView.as_view(), name='detail'),
]
