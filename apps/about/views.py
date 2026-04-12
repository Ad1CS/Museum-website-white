from django.views.generic import TemplateView
from .models import AboutPage

class AboutView(TemplateView):
    template_name = 'about/about.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page'] = AboutPage.load()
        return ctx
