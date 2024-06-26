from django.views.generic import TemplateView, ListView


class OperatorSettingsTemplateView(TemplateView):
    template_name = 'apps/admin/operator/operator.html'
