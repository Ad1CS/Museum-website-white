from django.views.generic import ListView, DetailView
from django.db.models import Max, Q
from .models import FondItem, Fund, ArchiveCase, ItemType, Period


PERIOD_NAV = [
    {'value': Period.P1880, 'label': 'старая бойня', 'years': '1880–1931'},
    {'value': Period.P1931, 'label': 'период строительства и довоенной эксплуатации', 'years': '1931–1941'},
    {'value': Period.P1941, 'label': 'война', 'years': '1941–1945'},
    {'value': Period.P1945, 'label': 'послевоенное развитие', 'years': '1945–1991'},
    {'value': Period.P1991, 'label': 'постсоветский период', 'years': '1991–2007'},
    {'value': Period.P2007, 'label': 'наши дни', 'years': '2007–н.д.'},
]


class CatalogView(ListView):
    template_name = 'fond/catalog.html'
    context_object_name = 'items'
    paginate_by = 24

    def get_queryset(self):
        qs = FondItem.objects.filter(published=True).select_related('fund')
        q = self.request.GET.get('q', '')
        item_type = self.request.GET.get('type', '')
        period = self.request.GET.get('period', '')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) |
                           Q(kp_number__icontains=q))
        if item_type:
            qs = qs.filter(item_type=item_type)
        if period:
            qs = qs.filter(period=period)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['item_types'] = ItemType.choices
        ctx['periods'] = Period.choices
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_period'] = self.request.GET.get('period', '')
        ctx['total_count'] = FondItem.objects.filter(published=True).count()
        ctx['view_mode'] = 'catalog'
        ctx['period_nav'] = PERIOD_NAV
        return ctx


class FundsListView(ListView):
    template_name = 'fond/funds_list.html'
    context_object_name = 'funds'
    model = Fund

    def get_queryset(self):
        qs = Fund.objects.all()
        q = self.request.GET.get('q', '')
        period = self.request.GET.get('period', '')
        if q:
            qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
        if period:
            qs = qs.filter(period=period)
        return qs.order_by('category', 'period', 'code')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['view_mode'] = 'funds'
        ctx['period_nav'] = PERIOD_NAV
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_period'] = self.request.GET.get('period', '')
        return ctx


class FundDetailView(DetailView):
    template_name = 'fond/fund_detail.html'
    model = Fund
    context_object_name = 'fund'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inventories'] = self.object.inventories.prefetch_related('cases').all()
        personal_owner = self.object.personal_fund_of.filter(published=True).first()
        ctx['personal_owner'] = personal_owner
        item_order = ['created_at', 'pk'] if personal_owner else ['period', 'title']
        ctx['items'] = self.object.items.filter(published=True).order_by(*item_order)
        return ctx


class FondItemDetailView(DetailView):
    template_name = 'fond/item_detail.html'
    model = FondItem
    context_object_name = 'item'
    queryset = FondItem.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        item = self.object
        gallery_media = item.gallery_photos.filter(published=True).order_by('order', 'created_at')
        media_items = []
        if item.image:
            media_items.append({
                'src': item.image.url,
                'type': 'photo',
                'caption': item.title,
                'year': item.display_year,
                'photographer': item.author,
                'fond_url': '',
                'video_embed': '',
            })
        for media in gallery_media:
            if media.image and (not item.image or media.image.name != item.image.name):
                media_items.append({
                    'src': media.image.url,
                    'type': media.media_type,
                    'caption': media.caption,
                    'year': media.date_text,
                    'photographer': media.photographer,
                    'fond_url': '',
                    'video_embed': media.embed_url or '',
                })
        if item.back_image:
            media_items.append({
                'src': item.back_image.url,
                'type': 'photo',
                'caption': 'Оборотная сторона',
                'year': item.display_year,
                'photographer': item.author,
                'fond_url': '',
                'video_embed': '',
            })
        ctx['album_media'] = gallery_media
        ctx['media_items'] = media_items
        ctx['first_media'] = media_items[0] if media_items else None
        ctx['additional_media'] = media_items[1:]
        ctx['has_multiple_media'] = len(media_items) > 1
        ctx['main_media_index'] = 0 if media_items else None
        ctx['back_media_index'] = len(media_items) - 1 if item.back_image else None
        ctx['detail_text_rows'] = item.detail_text_rows_for_page()
        ctx['register_text'] = item.display_register_text
        inventory = item.archive_case.inventory if item.archive_case_id else None
        ctx['fond_inventory_label'] = inventory.number if inventory else ''
        ctx['fond_case_label'] = item.archive_case.number if item.archive_case_id else ''
        ctx['kp_number_display'] = (
            item.inventory_number.replace('КП', '').strip()
            if item.inventory_number else item.kp_number
        )
        ctx['related_items'] = FondItem.objects.filter(
            fund=self.object.fund, published=True
        ).exclude(pk=self.object.pk)[:4]
        return ctx


class CaseDetailView(DetailView):
    template_name = 'fond/case_detail.html'
    model = ArchiveCase
    context_object_name = 'case'


from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@staff_member_required
def bulk_upload_do(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    from apps.gallery.models import Album, Media as GalleryMedia
    from .models import FondItem
    item = get_object_or_404(FondItem, pk=item_id)
    images = request.FILES.getlist('images')
    album_title = f'Фонд #{item.pk}: {item.title[:90]}'
    album, _ = Album.objects.get_or_create(
        title=album_title,
        defaults={'published': True, 'description': f'Фотографии предмета фонда: {item.title}'},
    )
    max_order = GalleryMedia.objects.filter(album=album).aggregate(value=Max('order'))['value'] or 0
    created = []
    for i, img in enumerate(images):
        media = GalleryMedia.objects.create(
            album=album, media_type='photo', image=img,
            fond_item=item, caption='', order=max_order + i + 1, published=True,
        )
        created.append(media.pk)
        if i == 0 and not item.image:
            item.image = media.image.name
            item.save(update_fields=['image'])
        if i == 0 and not album.cover and media.image:
            album.cover = media.image.name
            album.save(update_fields=['cover'])
    return JsonResponse({'created': len(created), 'ids': created})
