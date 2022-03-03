from django.urls import resolve
from django.utils.text import slugify


def get_slug(obj, *args):
    items = ''.join(
        map(lambda item: str(item) + ' ', args)
    )
    slug = slugify(items)[:100]
    return obj.__class__.objects.filter(slug=slug).exists(), slug


def is_url(request, *, url_name):
    actual_url_name = resolve(request.path_info).url_name

    return bool(actual_url_name == url_name)
