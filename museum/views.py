from django.views.generic import TemplateView
from apps.news.models import NewsPost
from apps.fond.models import FondItem
from apps.gallery.models import Photo


class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx['latest_news'] = list(NewsPost.objects.filter(published=True).order_by('-date')[:3])
        except Exception:
            ctx['latest_news'] = []
        try:
            ctx['recent_items'] = list(FondItem.objects.filter(published=True).select_related('fund').order_by('-created_at')[:6])
        except Exception:
            ctx['recent_items'] = []
        try:
            ctx['random_photos'] = list(Photo.objects.filter(published=True).order_by('?')[:8])
        except Exception:
            ctx['random_photos'] = []
        return ctx


class HistoryTimelineView(TemplateView):
    template_name = 'history/timeline.html'
