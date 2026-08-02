from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.fond.models import ArchiveCase, FondItem, Fund
from apps.gallery.models import Album
from apps.library.models import LibraryItem
from apps.mapblock.models import Building
from apps.news.models import NewsPost
from apps.staff.models import StaffMember


class BaseMuseumSitemap(Sitemap):
    protocol = 'https'


class StaticViewSitemap(BaseMuseumSitemap):
    items_config = [
        ('home', 'daily', 1.0),
        ('about:page', 'monthly', 0.7),
        ('history', 'monthly', 0.8),
        ('library:home', 'weekly', 0.8),
        ('gallery:home', 'weekly', 0.8),
        ('fond:catalog', 'weekly', 0.9),
        ('fond:funds_list', 'weekly', 0.8),
        ('staff:list', 'weekly', 0.8),
        ('mapblock:map', 'monthly', 0.8),
        ('mapblock:plans', 'monthly', 0.7),
        ('news:list', 'weekly', 0.7),
    ]

    def items(self):
        return self.items_config

    def location(self, item):
        return reverse(item[0])

    def changefreq(self, item):
        return item[1]

    def priority(self, item):
        return item[2]


class FundSitemap(BaseMuseumSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Fund.objects.all().order_by('category', 'period', 'code')

    def lastmod(self, item):
        return item.created_at


class ArchiveCaseSitemap(BaseMuseumSitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ArchiveCase.objects.select_related('inventory', 'inventory__fund').order_by(
            'inventory__fund__code', 'inventory__number', 'number'
        )

    def lastmod(self, item):
        return item.date_end or item.date_start


class FondItemSitemap(BaseMuseumSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return FondItem.objects.filter(published=True).select_related('fund', 'archive_case').order_by('-updated_at')

    def lastmod(self, item):
        return item.updated_at


class AlbumSitemap(BaseMuseumSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Album.objects.filter(published=True).order_by('order', 'title')

    def lastmod(self, item):
        return item.created_at


class LibraryItemSitemap(BaseMuseumSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return LibraryItem.objects.filter(published=True).order_by('-created_at')

    def lastmod(self, item):
        return item.created_at


class StaffMemberSitemap(BaseMuseumSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return StaffMember.objects.filter(published=True).order_by('last_name', 'first_name')

    def lastmod(self, item):
        return item.created_at


class BuildingSitemap(BaseMuseumSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Building.objects.filter(published=True).order_by('order', 'name')


class NewsPostSitemap(BaseMuseumSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return NewsPost.objects.filter(published=True).order_by('-date')

    def lastmod(self, item):
        return item.date


sitemaps = {
    'static': StaticViewSitemap,
    'funds': FundSitemap,
    'cases': ArchiveCaseSitemap,
    'fond_items': FondItemSitemap,
    'gallery_albums': AlbumSitemap,
    'library_items': LibraryItemSitemap,
    'staff': StaffMemberSitemap,
    'buildings': BuildingSitemap,
    'news': NewsPostSitemap,
}