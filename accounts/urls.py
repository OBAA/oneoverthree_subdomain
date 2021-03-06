from django.conf.urls import url, include

from dashboard.views import DashboardHomeView, OrderProcessingView

from marketing.views import MarketingPreferenceUpdateView, subscribe_to_notifications

from store.views import UserProductHistoryView

from orders.views import OrderListView, OrderDetailView, OrderCompletedView

from . import views

app_name = 'accounts'

urlpatterns = [

    url(r'^$', views.AccountHomeView.as_view(), name='home'),

    url(r'^details/$', views.AccountDetailsView.as_view(), name='details'),
    url(r'^details/update/$', views.UserDetailUpdateView.as_view(), name='details-update'),

    url(r'^dashboard/', include("dashboard.urls", namespace='dashboard')),

    url(r'^email/resend-activation/$', views.AccountEmailActivateView.as_view(), name='resend-activation'),
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', views.AccountEmailActivateView.as_view(), name='email-activate'),

    url(r'^history/products/$', UserProductHistoryView.as_view(), name='user-product-history'),

    url(r'^orders/$', OrderListView.as_view(), name='orders'),
    url(r'^orders/order-update/$', OrderCompletedView.as_view(), name='order-complete'),
    url(r'^orders/(?P<order_id>[0-9A-Za-z]+)/$', OrderDetailView.as_view(), name='order-details'),

    # url(r'^settings/$', views.AccountSettingsView.as_view(), name='settings'),
    url(r'^settings/$', MarketingPreferenceUpdateView.as_view(), name='newsletter-subscribe-update'),
    url(r'^settings/newsletter/$', subscribe_to_notifications, name='newsletter-subscribe'),
]


