from django.views.generic import ListView, TemplateView

from apps.models import Product


class OperatorindexTemplateView(ListView):
    template_name = 'apps/admin/apps/operator.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_operators'] = Product.objects.all()
        return context

    def get_queryset(self):
        return Product.objects.all()


class OperatorOrderTemplateView(TemplateView):
    template_name = 'apps/admin/apps/operator/operator_order.html'


class OperatorNewTemplateView(TemplateView):
    template_name = 'apps/admin/apps/operator/operator_new.html'

