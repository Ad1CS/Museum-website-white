from dataclasses import dataclass

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse


@dataclass(frozen=True)
class CanonicalSite:
    domain: str
    name: str


def robots_txt(request):
    body = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        f'Sitemap: {settings.SEO_CANONICAL_URL}/sitemap.xml',
        '',
    ])
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def google_site_verification(request):
    return HttpResponse(
        'google-site-verification: google0efda1dccc19138d.html\n',
        content_type='text/html; charset=utf-8',
    )


def sitemap_xml(request, sitemaps):
    page = request.GET.get('p', 1)
    canonical_site = CanonicalSite(
        domain=settings.SEO_CANONICAL_DOMAIN,
        name=settings.SEO_CANONICAL_DOMAIN,
    )
    urls = []

    for sitemap_class in sitemaps.values():
        sitemap = sitemap_class() if callable(sitemap_class) else sitemap_class
        try:
            urls.extend(
                sitemap.get_urls(
                    page=page,
                    site=canonical_site,
                    protocol=settings.SEO_CANONICAL_SCHEME,
                )
            )
        except EmptyPage:
            raise Http404(f'Sitemap page {page} is empty')
        except PageNotAnInteger:
            raise Http404(f'Sitemap page {page} is not an integer')

    return TemplateResponse(
        request,
        'sitemap.xml',
        {'urlset': urls},
        content_type='application/xml; charset=utf-8',
    )
