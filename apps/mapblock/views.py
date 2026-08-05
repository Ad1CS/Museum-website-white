from django.views.generic import TemplateView, DetailView, ListView

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
            class _FallbackSettings:
                zoom = 0
                center_x = 3684
                center_y = 2072
                min_zoom = -2
                max_zoom = 3
                building_zoom = 1
                territory_zoom_adjust = 0
                show_territory = True
                territory_x = 3684
                territory_y = 2072
                territory_w = 2000
                territory_h = 1500
                territory_rotation = 0
                territory_mirror_x = False
                territory_mirror_y = False
                territory_clip_path = ''

            ctx['map_settings'] = _FallbackSettings()
        return ctx


class BuildingDetailView(DetailView):
    template_name = 'mapblock/building.html'
    model = Building
    context_object_name = 'building'
    slug_url_kwarg = 'slug'
    queryset = Building.objects.filter(published=True)


class PlansView(ListView):
    template_name = 'mapblock/plans.html'
    context_object_name = 'buildings'

    def get_queryset(self):
        return Building.objects.filter(published=True).order_by('order', 'name')
