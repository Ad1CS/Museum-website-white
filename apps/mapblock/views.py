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
                zoom = 0
                center_x = 3684
                center_y = 2072
                min_zoom = -2
                max_zoom = 3
                building_zoom = 1
            ctx['map_settings'] = _FallbackSettings()
        return ctx


class BuildingDetailView(DetailView):
    template_name = 'mapblock/building.html'
    model = Building
    context_object_name = 'building'
    slug_url_kwarg = 'slug'
