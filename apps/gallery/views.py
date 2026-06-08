from django.views.generic import TemplateView, DetailView
from .models import Album, Media, GalleryPeriod
import re

class GalleryHomeView(TemplateView):
    template_name = "gallery/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periods = []
        # Get regular periods
        for gp in GalleryPeriod.objects.all():
            albums = gp.albums.filter(published=True, is_newsreel=False)
            if albums.exists():
                # Extract year range from title if present, e.g. "Name (1880-1931)"
                periods.append({"label": gp.title, "years": gp.date_range, "albums": albums})
        
        # Get newsreel albums separately
        newsreel_albums = Album.objects.filter(published=True, is_newsreel=True)
        if newsreel_albums.exists():
            periods.append({"label": "Кинохроника", "years": "", "albums": newsreel_albums})
            
        ctx["periods"] = periods
        return ctx

class AlbumDetailView(DetailView):
    model = Album
    template_name = "gallery/album_detail.html"
    context_object_name = "album"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["photos"] = self.object.media.filter(published=True).order_by("order", "created_at")
        return ctx

