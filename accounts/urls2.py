from django.urls import path

from accounts.fronts import WebAuthorizationRecordListView, DomainuthorizedListListView, DomainuthorizedListCreateView, \
    DomainuthorizedListUpdateView, domainthorized_delete

urlpatterns = [
    path('domainthorized/list/', DomainuthorizedListListView.as_view(), name='domainthorized_list'),
    path('webrecord/list/', WebAuthorizationRecordListView.as_view(), name='webrecord_list'),
    path('domainthorized/add/', DomainuthorizedListCreateView.as_view(), name='domainthorized_add'),
    path('domainthorized/update/<int:pk>', DomainuthorizedListUpdateView.as_view(), name='domainthorized_update'),
    path('domainthorized/delete/<int:pk>/', domainthorized_delete, name='domainthorized_delete'),

]