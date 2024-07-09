from django.views.generic import ListView, TemplateView, DetailView
from apps.models import Product, Order, Region, District


class OperatorIndexTemplateView(ListView):
    template_name = 'apps/admin/apps/operator.html'


class OperatorOrderTemplateView(TemplateView):
    template_name = 'apps/admin/apps/operator_order.html'


class OperatorNewTemplateView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/admin/apps/operator_new.html'
    context_object_name = 'product_operators'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operator_regions'] = Region.objects.all()
        context['operator_districts'] = District.objects.all()
        return context


class OrderOperatorDetailView(DetailView):
    model = Order.objects.all()
    template_name = 'apps/admin/apps/operator_new.html'
    context_object_name = 'Operator_Orders'
    pk_url_kwarg = 'order_id'

