from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView

from apps.forms import OrderModelForm, StreamOrderModelForm
from apps.models.products import Product, Category, Order, Stream


class ProductListView(ListView):
    paginate_by = 3
    model = Product
    template_name = 'apps/products/index.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(FormView, DetailView):
    model = Product
    template_name = 'apps/products/product_detail.html'
    form_class = OrderModelForm

    def form_valid(self, form):
        order = form.save(commit=False)
        order.user = self.request.user
        order = form.save()
        return redirect('product_success', pk=order.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stream_id = self.kwargs.get(self.pk_url_kwarg, '')
        context['stream_id'] = self.kwargs.get(self.pk_url_kwarg, '')

        if stream_id:
            stream = get_object_or_404(Stream, pk=stream_id)
            adjusted_price = self.get_adjusted_price(stream.product.price, stream.discount, stream.benefit)
            context['adjusted_price'] = adjusted_price
        return context

    def get_adjusted_price(self, original_price, discount, benefit=None):
        if benefit is None:
            benefit = 0
        adjusted_price = original_price - discount + benefit
        return adjusted_price

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)

        if pk is not None:
            stream = get_object_or_404(Stream.objects.all(), pk=pk)
            stream.counter += 1
            stream.save()
            return stream.product

        product = get_object_or_404(Product.objects.all(), slug=slug)
        return product


class OrderProductSuccessDetailView(DetailView):
    model = Order
    template_name = 'apps/products/order_product.html'
    context_object_name = 'order'
    slug_field = 'slug'


class OrderListView(ListView):
    paginate_by = 5
    template_name = 'apps/products/orders.html'
    queryset = Order.objects.order_by('created_at')
    context_object_name = 'orders'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MarketProductListView(ListView):
    model = Product
    template_name = 'apps/products/market.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category == 'top_product':
            queryset = self.top_products()
        if category:
            queryset = queryset.filter(category__slug=category)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def top_products(self):
        seven_days_ago = timezone.now() - timedelta(days=7)
        product_ids = (
            Order.objects.filter(created_at__gte=seven_days_ago, status=Order.Status.DELIVERED)
            .values('product_id').annotate(total_quantity=Sum('count'))
            .order_by('-total_quantity').values_list('product_id', flat=True)[:5]
        )
        return Product.objects.filter(id__in=product_ids)


class StreamOrderFormView(LoginRequiredMixin, FormView):
    template_name = 'apps/products/market.html'
    form_class = StreamOrderModelForm

    def form_valid(self, form):
        stream = form.save(commit=False)
        stream.user = self.request.user
        stream.save()
        return redirect('stream_order_list')


class StreamOrderListView(LoginRequiredMixin, ListView):
    model = Stream
    template_name = 'apps/products/stream.html'
    context_object_name = 'streams'

    def get_queryset(self):
        return Stream.objects.filter(user=self.request.user)


class StatsListView(LoginRequiredMixin, ListView):
    template_name = 'apps/admin/stats.html'
    context_object_name = 'stats'

    def get_queryset(self):
        period = self.request.GET.get('period', 'all')
        today = timezone.now().date()
        date_filters = {
            'today': Q(orders__created_at__date=today),
            'last_day': Q(orders__created_at__date=today - timedelta(days=-1)),
            'weekly': Q(orders__created_at__date__gte=today - timedelta(days=today.weekday() + 7)),
            'monthly': Q(orders__created_at__date__gte=today.replace(day=1) - relativedelta(months=1)),
            'all': Q()
        }

        queryset = Stream.objects.annotate(
            orders_new=Count('orders', filter=Q(orders__status=Order.Status.NEW)),
            orders_visit=Count('orders', filter=Q(orders__status=Order.Status.VISIT)),
            orders_ready=Count('orders', filter=Q(orders__status=Order.Status.READY)),
            orders_delivery=Count('orders', filter=Q(orders__status=Order.Status.DELIVERY)),
            orders_delivered=Count('orders', filter=Q(orders__status=Order.Status.DELIVERED)),
            orders_canceled=Count('orders', filter=Q(orders__status=Order.Status.CANCELED)),
            orders_archived=Count('orders', filter=Q(orders__status=Order.Status.ARCHIVED)),
            orders_phone=Count('orders', filter=Q(orders__status=Order.Status.PHONE))
        ).select_related('product').filter(date_filters.get(period, Q()))

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        totals = queryset.aggregate(
            total_orders_new=Sum('orders_new'),
            total_orders_visit=Sum('orders_visit'),
            total_orders_ready=Sum('orders_ready'),
            total_orders_delivery=Sum('orders_delivery'),
            total_orders_delivered=Sum('orders_delivered'),
            total_orders_canceled=Sum('orders_canceled'),
            total_orders_archived=Sum('orders_archived'),
            total_orders_phone=Sum('orders_phone')
        )
        context.update(totals)
        return context


class UserRequestsListView(LoginRequiredMixin, ListView):
    template_name = 'apps/admin/requests.html'
    queryset = Order.objects.select_related('stream', 'region').order_by('created_at')
    context_object_name = 'orders'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class WishesUserListView(ListView):
    template_name = 'apps/products/lake.html'
    model = Product
    context_object_name = 'wishes'
