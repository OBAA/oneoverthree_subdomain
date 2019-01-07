from django.conf.urls import url

from . import views


app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.DashboardHomeView.as_view(), name='home'),

    url(r'^orders/$', views.DashboardOrdersView.as_view(), name='orders'),
    url(r'^product-list/$', views.DashboardProductListView.as_view(), name='products'),
    url(r'^store-image-upload/$', views.StoreImageUploadView.as_view(), name='update-store-image'),
    url(r'^add-product/$', views.AddProductView.as_view(), name='add-product'),
    url(r'^update-product/$', views.UpdateProductFormView.as_view(), name='update-product'),
    url(r'^delete-product/$', views.DeleteProductView.as_view(), name='delete-product'),
    url(r'^order-processing/$', views.OrderProcessingView.as_view(), name='order-processing'),
    url(r'^order-shipped/$', views.OrderShippedView.as_view(), name='order-shipped'),
]
