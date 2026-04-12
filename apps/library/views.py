from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import LibraryItem


class LibraryHomeView(ListView):
    template_name = 'library/home.html'
    context_object_name = 'items'

    def get_queryset(self):
        qs = LibraryItem.objects.filter(published=True)
        cat = self.request.GET.get('cat', '')
        q = self.request.GET.get('q', '')
        if cat in ('book', 'periodical'):
            qs = qs.filter(category=cat)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_cat'] = self.request.GET.get('cat', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['books_count'] = LibraryItem.objects.filter(published=True, category='book').count()
        ctx['periodicals_count'] = LibraryItem.objects.filter(published=True, category='periodical').count()
        return ctx


class LibraryDetailView(DetailView):
    template_name = 'library/detail.html'
    model = LibraryItem
    context_object_name = 'item'
    queryset = LibraryItem.objects.filter(published=True)
