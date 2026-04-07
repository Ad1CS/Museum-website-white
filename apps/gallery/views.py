from django.views.generic import TemplateView, DetailView
from .models import Album, Media, HistoricalPeriod


class GalleryHomeView(TemplateView):
    template_name = 'gallery/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            periods = []
            for code, label in HistoricalPeriod.choices:
                albums = Album.objects.filter(period=code, published=True)
                if albums.exists():
                    periods.append({'label': label, 'albums': albums})
            ctx['periods'] = periods
        except Exception:
            ctx['periods'] = []
        try:
            ctx['random_photos'] = list(Media.objects.filter(
                published=True, media_type='photo'
            ).exclude(image='').order_by('?')[:18])
        except Exception:
            ctx['random_photos'] = []
        return ctx


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['photos'] = self.object.media.filter(published=True).order_by('order', 'created_at')
        ctx['other_albums'] = Album.objects.filter(
            period=self.object.period, published=True
        ).exclude(pk=self.object.pk)
        return ctx
