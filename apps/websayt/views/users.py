from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import activate, gettext_lazy as _
from django.views.generic import UpdateView, TemplateView, ListView, FormView

from apps.websayt.forms import RegisterModelForm, LoginModelForm, UserSettingsImageModelForm, UserSettingsModelForm, \
    UserSettingsPasswordChangeForm, PaymeModelForm
from apps.websayt.models.products import District, Stream, Competition, Order, SiteSetting, Region
from apps.websayt.models.users import User, PaymeRequest
from apps.websayt.utils import resize_image


class RegistrationView(FormView):
    template_name = 'apps/auth/register.html'
    form_class = RegisterModelForm
    success_url = reverse_lazy('login_page')

    def form_valid(self, form):
        user = form.save(commit=False)
        status = form.cleaned_data.get('status')
        user.save()
        login(self.request, user)
        if status == User.Status.SELLER:
            messages.success(self.request, "Magazin muvaffaqiyatli yaratildi!")
            return redirect('login_page')
        elif status == User.Status.USERS:
            messages.success(self.request, "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!")
            return redirect('login_page')
        else:
            return super().form_valid(form)


class LoginUserView(FormView):
    template_name = 'apps/auth/login.html'
    form_class = LoginModelForm
    success_url = reverse_lazy('product_list_page')

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            login(self.request, user)
            if user.status == User.Status.SELLER:
                return redirect('dashboard')
            elif user.status == User.Status.USERS:
                return redirect('product_list_page')
            elif user.status == User.Status.OPERATOR:
                return redirect('operator_page')
            else:
                return redirect('product_list_page')
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Kiritilgan ma'lumotlarda xatolik bor")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect('login_page')


class UserSettingsImageUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsImageModelForm
    template_name = 'apps/admin/settings.html'
    success_url = reverse_lazy('user_settings_update')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        response_data = {}

        if 'avatar' in form.files:
            avatar = form.files['avatar']
            resized_avatar = resize_image(avatar, size=(300, 300))
            if resized_avatar:
                user.avatar.save(resized_avatar.name, resized_avatar)
                response_data['avatar_url'] = user.avatar.url

        if 'banner' in form.files:
            banner = form.files['banner']
            resized_banner = resize_image(banner, size=(1200, 300))
            if resized_banner:
                user.banner.save(resized_banner.name, resized_banner)
                response_data['banner_url'] = user.banner.url

        user.save()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(response_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)


class UserSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsModelForm
    template_name = 'apps/admin/settings.html'
    success_url = reverse_lazy('user_settings_update')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        if 'avatar' in self.request.FILES:
            form.instance.avatar = self.request.FILES['avatar']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        if self.object.region:
            context['districts'] = District.objects.filter(region=self.object.region)
        return context


def get_districts(request):
    region_id = request.GET.get('region_id')
    if region_id:
        districts = District.objects.filter(region_id=region_id).values('id', 'name')
        districts_list = list(districts)  # Convert the QuerySet to a list
    else:
        districts_list = []

    return JsonResponse(districts_list, safe=False)


class UserSettingsPassword(LoginRequiredMixin, PasswordChangeView):
    template_name = 'apps/admin/settings.html'
    form_class = UserSettingsPasswordChangeForm
    success_url = reverse_lazy('user_settings_update')

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class CompetitionListView(LoginRequiredMixin, ListView):
    template_name = 'apps/admin/competition.html'
    context_object_name = 'competitions'
    model = Stream

    def get_queryset(self):
        return super().get_queryset().prefetch_related('orders')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        referral_competition = Competition.objects.filter(is_active=True).first()

        if referral_competition:
            stream_orders = Order.objects.filter(
                created_at__gte=referral_competition.start_date,
                created_at__lte=referral_competition.end_date,
                status=Order.Status.DELIVERED
            ).values(
                'referral_user__first_name'
            ).annotate(
                total_orders=Sum('count')
            ).order_by('-total_orders')
        else:
            stream_orders = []

        context['referral_competition'] = referral_competition
        context['stream_orders'] = stream_orders
        return context


class PaymeFormView(LoginRequiredMixin, FormView):
    form_class = PaymeModelForm
    template_name = 'apps/admin/payment.html'

    def form_valid(self, form):
        user = self.request.user
        amount = form.cleaned_data.get('amount')

        site_setting = SiteSetting.objects.first()
        if not site_setting:
            messages.error(self.request, _("Site error"))
            return redirect('withdraw')

        minimal_sum = site_setting.minimal_sum
        if user.main_balance < amount or amount < minimal_sum:
            messages.error(self.request, _("You don't have enough money"))
            return redirect('withdraw')

        user.main_balance -= amount
        user.save()
        payme_request = form.save(commit=False)
        payme_request.user = user
        payme_request.save()
        messages.success(self.request, _('Payment made successfully!'))
        return redirect('withdraw')


class PaymeListView(LoginRequiredMixin, ListView):
    template_name = 'apps/admin/payment.html'
    model = PaymeRequest
    context_object_name = 'payments'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        total_paid_amount = PaymeRequest.objects.filter(status=PaymeRequest.Status.PAID).aggregate(total=Sum('amount'))[
            'total']
        context['total_paid_amount'] = total_paid_amount
        return context


class ProfileTemplateView(TemplateView):
    template_name = 'apps/admin/profile.html'


class FavoritesTemplateView(TemplateView):
    template_name = 'apps/admin/favorites.html'


def change_language(request, lang_code):
    activate(lang_code)
    request.session['django_language'] = lang_code
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    response = HttpResponseRedirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response
