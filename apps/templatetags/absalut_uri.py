from django import template

register = template.Library()


@register.filter()
def get_base_url(url: str):
    abs_url = url.split('/')
    return '/'.join(abs_url[:3])
