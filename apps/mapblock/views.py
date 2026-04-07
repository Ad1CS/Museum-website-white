from django.views.generic import TemplateView, DetailView
from .models import Building, MapSettings


class MapView(TemplateView):
    template_name = 'mapblock/map.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx['buildings'] = list(Building.objects.filter(published=True))
        except Exception:
            ctx['buildings'] = []
        try:
            ctx['map_settings'] = MapSettings.get()
        except Exception:
            # Fallback if migration hasn't run yet
            class _FallbackSettings:
                zoom = 17
                center_lat = 59.8247
                center_lng = 30.3492
            ctx['map_settings'] = _FallbackSettings()
        return ctx


class BuildingDetailView(DetailView):
    template_name = 'mapblock/building.html'
    model = Building
    context_object_name = 'building'
    slug_url_kwarg = 'slug'
