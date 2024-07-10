from django.views.generic import ListView, TemplateView, DetailView
from apps.models import Product, Order, Region, District


class OperatorIndexTemplateView(TemplateView):
    template_name = 'apps/operator/operator.html'


class OperatorOrderListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/operator/operator_order.html'
    context_object_name = 'products_adds'


class OperatorNewListView(ListView):
    model = Order
    template_name = 'apps/operator/operator_new.html'

    def get_queryset(self):
        context = super().get_queryset()
        product = self.request.GET.getlist('product')
        region = self.request.GET.get('region')
        district = self.request.GET.get('district')

        if product:
            context = context.filter(product__in=product)
        if region:
            context = context.filter(district__region_id=region)
        if district:
            context = context.filter(district_id=district)
        context = context.order_by('created_at')
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_operators'] = Product.objects.all()
        context['operator_regions'] = Region.objects.all()
        context['operator_districts'] = District.objects.all()
        context['operator_orders'] = Order.objects.all()
        return context
