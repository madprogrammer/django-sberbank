from django.conf.urls import url
from sberbank import views

urlpatterns = [  # noqa: pylint=invalid-name
    url('payment/callback', views.callback),
    url('payment/success', views.redirect, {'kind': 'success'}),
    url('payment/fail', views.redirect, {'kind': 'fail'}),
    url('payment/status/(?P<uid>[^/]+)/', views.StatusView.as_view()),
    url('payment/bindings/(?P<client_id>[^/]+)/', views.BindingsView.as_view()),
    url('payment/binding/(?P<binding_id>[^/]+)/', views.BindingView.as_view()),
    url('payment/history/(?P<client_id>[^/]+)/', views.GetHistoryView.as_view()),
]
