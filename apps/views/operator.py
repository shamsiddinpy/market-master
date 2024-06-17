from django.views.generic import TemplateView


class OperatorSettingsTemplateView(TemplateView):
    template_name = 'apps/admin/operator/operator.html'
