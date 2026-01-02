from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

"""
**Create CategoryPage model**
   - File: `app/shop/models.py`
   - Extends: `wagtail.models.Page`
   - Fields:
     - `description` (RichTextField, blank=True)
     - `icon` (ForeignKey to wagtailimages.Image, optional)
     - `featured` (BooleanField, default=False)
   - Content panels:
     - Basic: title (inherited from Page), description, icon, featured
   - Settings panels:
     - Promote tab: slug (auto-populating), SEO fields
   - Parent page types: `HomePage` or self (for subcategories)
   - Subpage types: `ProductPage`, `CategoryPage` (allow subcategories)
   - Methods:
     - `get_products()`: Returns child ProductPage objects
     - `get_context()`: Add products and pagination to template
     """


class ShopCategoryPage(Page):
    description = RichTextField(blank=True)
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("featured"),
    ]

    parent_page_types = ["home.HomePage"]
    # subpage_types = ["app.shop.ProductPage"] hidden for now

    # implement later
    # def get_products(self):
    #     return ProductPage.objects.child_of(self).live()

    # implement later
    # def get_context(self, request):
    #     context = super().get_context(request)
    #     products = self.get_products()
    #     paginator = Paginator(products, 10)  # Show 10 products per page
    #     page_number = request.GET.get("page")
    #     page_obj = paginator.get_page(page_number)
    #     context["products"] = page_obj
    #     return context
