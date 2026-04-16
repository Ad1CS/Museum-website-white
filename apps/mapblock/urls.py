from django.urls import path
from . import views

app_name = 'mapblock'

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('<slug:slug>/', views.BuildingDetailView.as_view(), name='building'),
]
