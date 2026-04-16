from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import FondItem, Fund, ArchiveCase, ItemType, Period


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
        return ctx


class FundsListView(ListView):
    template_name = 'fond/funds_list.html'
    context_object_name = 'funds'
    model = Fund

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['view_mode'] = 'funds'
        return ctx


class FundDetailView(DetailView):
    template_name = 'fond/fund_detail.html'
    model = Fund
    context_object_name = 'fund'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inventories'] = self.object.inventories.prefetch_related('cases').all()
        return ctx


class FondItemDetailView(DetailView):
    template_name = 'fond/item_detail.html'
    model = FondItem
    context_object_name = 'item'
    queryset = FondItem.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
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
    album_title = f'Фонд: {item.title[:100]}'
    album, _ = Album.objects.get_or_create(
        title=album_title,
        defaults={'period': item.period or 'modern', 'published': True,
                  'description': f'Фотографии предмета фонда: {item.title}'},
    )
    max_order = GalleryMedia.objects.filter(album=album).order_by('-order').values_list('order', flat=True).first() or 0
    created = []
    for i, img in enumerate(images):
        media = GalleryMedia.objects.create(
            album=album, media_type='photo', image=img,
            fond_item=item, caption='', order=max_order + i + 1, published=True,
        )
        created.append(media.pk)
        if i == 0 and not item.image:
            item.image = img
            item.save(update_fields=['image'])
    return JsonResponse({'created': len(created), 'ids': created})
