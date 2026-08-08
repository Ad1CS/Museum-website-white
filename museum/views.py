from urllib.parse import urlparse

from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from apps.news.models import NewsPost
from apps.fond.models import FondItem
from apps.gallery.models import Photo
from apps.history.models import HistoryTextBlock
from .models import HomeBackground, HomeBackgroundSettings


class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_news'] = list(NewsPost.objects.filter(published=True).order_by('-date')[:3])
        ctx['recent_items'] = list(FondItem.objects.filter(published=True).select_related('fund').order_by('-created_at')[:6])
        ctx['random_photos'] = list(Photo.objects.filter(published=True).order_by('-created_at')[:8])
        try:
            backgrounds = list(HomeBackground.objects.filter(active=True).only('image', 'title').order_by('order', '-created_at'))
        except Exception:
            backgrounds = []

        urls = []
        seen_urls = set()
        for background in backgrounds:
            try:
                url = background.image.url
            except ValueError:
                continue
            if url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)

        try:
            settings = HomeBackgroundSettings.objects.first()
        except Exception:
            settings = None

        interval_seconds = settings.interval_seconds if settings else 8
        slideshow_enabled = bool(settings and settings.enabled and len(urls) > 1)
        ctx['home_background_urls'] = urls
        ctx['home_background_slideshow_enabled'] = slideshow_enabled
        ctx['home_background_interval_ms'] = max(2, interval_seconds) * 1000
        return ctx


class HistoryTimelineView(TemplateView):
    template_name = 'history/timeline.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['history_text_blocks'] = list(
            HistoryTextBlock.objects.filter(published=True).order_by('order', 'id')
        )
        return ctx


def _display_path(path):
    """Label for the header breadcrumb — without the slashes wrapping the path."""
    return path.strip('/') or 'главная'


def _not_found_context(request, current_path=None, include_referrer=True):
    referrer = request.META.get('HTTP_REFERER', '')
    previous_path = ''
    if include_referrer and referrer:
        parsed = urlparse(referrer)
        previous_path = parsed.path or '/'
        if parsed.query:
            previous_path = f'{previous_path}?{parsed.query}'

    current = current_path or request.get_full_path()
    return {
        'previous_path': previous_path,
        'previous_label': _display_path(previous_path) if previous_path else '',
        'current_path': current,
        'current_label': _display_path(current),
    }


def page_not_found(request, exception=None):
    return render(request, '404.html', _not_found_context(request), status=404)


def page_404(request):
    context = _not_found_context(request, current_path='404', include_referrer=False)
    return render(request, '404.html', context, status=404)


def legacy_404_preview_redirect(request):
    return redirect('page_404', permanent=True)
