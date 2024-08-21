from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core.cache import cache
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import activate, gettext_lazy as _
from django.views import View
from django.views.generic import UpdateView, TemplateView, ListView, FormView

from apps.forms import UserSettingsModelForm, UserSettingsImageModelForm, UserSettingsPasswordChangeForm, \
    LoginModelForm, PaymeModelForm
from apps.models import User, Region, District, Order, Stream, Competition, SiteSetting, PaymeRequest
from apps.utils import resize_image


class LoginUserView(FormView):
    template_name = 'apps/auth/login.html'
    form_class = LoginModelForm
    success_url = reverse_lazy('product_list_page')

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            if user.status == user.Status.OPERATOR:
                login(self.request, user)
                return redirect('operator_new')
            else:
                login(self.request, user)
                return redirect('product_list_page')
        return super().form_valid(form)


class LoginBotTemplateView(TemplateView):
    template_name = 'apps/auth/login_with_tlg_bot.html'


class LoginCheckView(View):
    def post(self, request, *args, **kwargs):
        code = self.request.POST.get('code', '')
        if len(code) != 6:
            return JsonResponse({'message': 'error code'}, status=400)
        phone = cache.get(code)
        if phone is None:
            return JsonResponse({'message': 'expired code'}, status=400)
        user = User.objects.get(phone=phone)
        login(request, user)
        return JsonResponse({'message': 'OK'})


class UserSettingsImageUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsImageModelForm
    template_name = 'apps/admin/settings.html'
    success_url = reverse_lazy('settings_images_update')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)

        if 'avatar' in form.files:
            avatar = form.files['avatar']
            resized_avatar = resize_image(avatar, size=(300, 300))
            if resized_avatar:
                user.avatar.save(resized_avatar.name, resized_avatar)

        if 'banner' in form.files:
            banner = form.files['banner']
            resized_banner = resize_image(banner, size=(1200, 300))
            if resized_banner:
                user.banner.save(resized_banner.name, resized_banner)

        user.save()
        return super().form_valid(form)


class UserSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsModelForm
    template_name = 'apps/admin/settings.html'
    success_url = reverse_lazy('user_settings_update')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
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
    success_url = reverse_lazy('settings_update_password')

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
        form.save()
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
    # Tilni faollashtirish
    activate(lang_code)
    request.session['django_language'] = lang_code

    # Hozirgi sahifaga qaytarish
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    response = HttpResponseRedirect(next_url)

    # Cookie ga yozish
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    return response
