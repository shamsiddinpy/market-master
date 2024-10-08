from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()


@register.filter()
def get_base_url(url: str):
    abs_url = url.split('/')
    return '/'.join(abs_url[:3])


@register.filter
def is_new_product(created_at):
    if timezone.now() - created_at <= timedelta(hours=24):
        return True
    else:
        return False


@register.filter()
def mask_card_number(card_number):
    if card_number and len(card_number) >= 8:
        return f"{card_number[:4]}{'*' * (len(card_number) - 8)}{card_number[-4:]}"
    return card_number
