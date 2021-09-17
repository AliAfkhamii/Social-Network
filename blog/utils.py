from django.utils.text import slugify


def get_slug(obj, *args):
    items = ''.join(
        map(lambda item: str(item)[:8] + ' ', args)
    )
    slug = slugify(items)
    return obj.__class__.objects.filter(slug=slug).exists(), slug
