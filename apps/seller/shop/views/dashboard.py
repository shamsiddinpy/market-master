from django.views.generic import TemplateView


class DashboardTemplateView(TemplateView):
    template_name = 'seller/saller_base.html'
