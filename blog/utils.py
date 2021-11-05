from django.utils.text import slugify


def get_slug(obj, *args):
    items = ''.join(
        map(lambda item: str(item) + ' ', args)
    )
    slug = slugify(items)[:100]
    return obj.__class__.objects.filter(slug=slug).exists(), slug
