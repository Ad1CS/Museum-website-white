from urllib.parse import urlparse

from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from apps.news.models import NewsPost
from apps.fond.models import FondItem
from apps.gallery.models import Photo


class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_news'] = list(NewsPost.objects.filter(published=True).order_by('-date')[:3])
        ctx['recent_items'] = list(FondItem.objects.filter(published=True).select_related('fund').order_by('-created_at')[:6])
        ctx['random_photos'] = list(Photo.objects.filter(published=True).order_by('-created_at')[:8])
        return ctx


class HistoryTimelineView(TemplateView):
    template_name = 'history/timeline.html'


def _not_found_context(request, current_path=None, include_referrer=True):
    referrer = request.META.get('HTTP_REFERER', '')
    previous_path = ''
    if include_referrer and referrer:
        parsed = urlparse(referrer)
        previous_path = parsed.path or '/'
        if parsed.query:
            previous_path = f'{previous_path}?{parsed.query}'

    return {
        'previous_path': previous_path,
        'current_path': current_path or request.get_full_path(),
    }


def page_not_found(request, exception=None):
    return render(request, '404.html', _not_found_context(request), status=404)


def page_404(request):
    context = _not_found_context(request, current_path='404', include_referrer=False)
    return render(request, '404.html', context, status=404)


def legacy_404_preview_redirect(request):
    return redirect('page_404', permanent=True)
