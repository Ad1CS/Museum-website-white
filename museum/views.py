from django.views.generic import TemplateView
from apps.news.models import NewsPost
from apps.fond.models import FondItem
from apps.gallery.models import Photo


class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        print("HomeView.get_context_data called")
        ctx = super().get_context_data(**kwargs)
        ctx['latest_news'] = list(NewsPost.objects.filter(published=True).order_by('-date')[:3])
        ctx['recent_items'] = list(FondItem.objects.filter(published=True).select_related('fund').order_by('-created_at')[:6])
        ctx['random_photos'] = list(Photo.objects.filter(published=True).order_by('-created_at')[:8])
        return ctx


class HistoryTimelineView(TemplateView):
    template_name = 'history/timeline.html'
