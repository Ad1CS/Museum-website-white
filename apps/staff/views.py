from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import StaffMember


class StaffListView(ListView):
    template_name = 'staff/list.html'
    context_object_name = 'members'

    def get_queryset(self):
        qs = StaffMember.objects.filter(published=True)
        q = self.request.GET.get('q', '')
        letter = self.request.GET.get('letter', '')
        if q:
            qs = qs.filter(
                Q(last_name__icontains=q) | Q(first_name__icontains=q) |
                Q(patronymic__icontains=q) | Q(role__icontains=q)
            )
        if letter:
            qs = qs.filter(last_name__istartswith=letter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # All first letters that have entries
        all_letters = StaffMember.objects.filter(published=True).exclude(last_name='').values_list('last_name', flat=True).distinct()
        ctx['available_letters'] = sorted(set(n[0].upper() for n in all_letters if n))
        ctx['alphabet'] = list('АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_letter'] = self.request.GET.get('letter', '')
        return ctx


class StaffDetailView(DetailView):
    template_name = 'staff/detail.html'
    model = StaffMember
    context_object_name = 'member'
    queryset = StaffMember.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['related_items'] = self.object.fond_items.filter(published=True)[:6]
        return ctx
