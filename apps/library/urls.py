from django.urls import path
from . import views
app_name = 'library'
urlpatterns = [
    path('', views.LibraryHomeView.as_view(), name='home'),
    path('<int:pk>/', views.LibraryDetailView.as_view(), name='detail'),
]
