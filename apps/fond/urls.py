from django.urls import path
from . import views

app_name = 'fond'

urlpatterns = [
    path('', views.CatalogView.as_view(), name='catalog'),
    path('funds/', views.FundsListView.as_view(), name='funds_list'),
    path('funds/<int:pk>/', views.FundDetailView.as_view(), name='fund_detail'),
    path('item/<int:pk>/', views.FondItemDetailView.as_view(), name='item_detail'),
    path('case/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
]
