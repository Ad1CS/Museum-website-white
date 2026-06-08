from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.GalleryHomeView.as_view(), name='home'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
]
