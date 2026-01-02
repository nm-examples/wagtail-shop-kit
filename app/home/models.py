from wagtail import __version__ as WAGTAIL_VERSION
from wagtail.models import Page

from app.shop.models import ShopCategoryPage


class HomePage(Page):
    def get_featured_categories(self):
        """Return featured shop categories"""
        return ShopCategoryPage.objects.live().filter(featured=True).order_by("title")

    def get_context(self, request):
        context = super().get_context(request)
        context["wagtail_version"] = WAGTAIL_VERSION
        context["featured_categories"] = self.get_featured_categories()
        return context
