from django.views.generic import ListView, DetailView
from .models import NewsPost


class NewsListView(ListView):
    template_name = 'news/list.html'
    context_object_name = 'posts'
    paginate_by = 10
    queryset = NewsPost.objects.filter(published=True)


class NewsDetailView(DetailView):
    template_name = 'news/detail.html'
    model = NewsPost
    context_object_name = 'post'
    queryset = NewsPost.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['recent'] = NewsPost.objects.filter(published=True).exclude(pk=self.object.pk)[:4]
        return ctx
