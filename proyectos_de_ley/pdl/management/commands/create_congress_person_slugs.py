"""
This command populates the database for Slug models which will include the
names and slugs for Congress men and women.

Run once a week.
"""
import six
import unicodedata

from django.core.management.base import BaseCommand

from pdl.models import Proyecto, Slug


class Command(BaseCommand):
    help = 'Creates Slugs for congress men and women names'

    def handle(self, *args, **options):
        all_current_slugs = [
            i["slug"]
            for i in Slug.objects.all().values("slug")
        ]
        person_names_bundled = Proyecto.objects.all().values("congresistas")
        all_names = []
        for item in person_names_bundled:
            names = item["congresistas"].split(";")
            all_names += [i.strip() for i in names]
        for name in set(all_names):
            ascii_name = convert_to_ascii(name)
            slug = slugify(name)
            if slug not in all_current_slugs:
                s = Slug(
                    ascii=ascii_name,
                    nombre=name,
                    slug=slug,
                )
                s.save()
                print("Created slug for {!r}".format(name))


def slugify(name):
    """Takes a person name and returns its slug.

    I wrote this function long time before I realized there were already slugify
    libraries ready to be used.

    This is the same function being used by the PDL scraper that generates
    the slug before saving the data directly into our database.
    """
    name = name.strip()
    name = name.replace(",", "").lower()
    name = name.split(" ")

    if len(name) > 2:
        i = 0
        slug = ""
        while i < 3:
            slug += name[i]
            if i < 2:
                slug += "_"
            i += 1
        try:
            slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore')
        except TypeError:
            slug = slug.decode('utf-8')
            slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore')

        if six.PY3 is True:
            slug = str(slug, encoding="utf-8")
        else:
            slug = slug.encode("utf-8")
        return slug + "/"


def convert_to_ascii(name):
    return unicodedata.normalize(
        'NFKD',
        name,
    ).encode('ascii', 'ignore').decode('utf-8')
