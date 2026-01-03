from django.core.paginator import Paginator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

"""
**Create ShopCategoryPage model**
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


class ShopIndexPage(Page):
    """
    Main shop page that displays all categories.
    Should be created once as a child of HomePage.
    """

    intro = RichTextField(
        blank=True, help_text="Optional introduction text for the shop"
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["shop.ShopCategoryPage"]
    max_count = 1  # Only one shop index page allowed

    def get_context(self, request):
        context = super().get_context(request)
        # Get all category pages that are children of this shop index
        categories = ShopCategoryPage.objects.child_of(self).live().order_by("title")
        context["categories"] = categories
        return context


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

    parent_page_types = ["shop.ShopIndexPage"]
    subpage_types = ["shop.ProductPage"]

    def get_products(self):
        """Returns child ProductPage objects"""
        return ProductPage.objects.child_of(self).live().order_by("-first_published_at")

    def get_context(self, request):
        context = super().get_context(request)
        products = self.get_products()
        paginator = Paginator(products, 12)  # Show 12 products per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["products"] = page_obj
        return context


class ProductImage(Orderable):
    """
    Inline image gallery for products.
    Allows multiple images per product with captions and ordering.
    """

    product = ParentalKey(
        "ProductPage", on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"Image for {self.product.title}"


class ProductPage(Page):
    """
    Individual product detail page.
    Products are children of CategoryPage in the page tree.
    """

    # Basic product info
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price in dollars",
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Stock Keeping Unit - leave blank to auto-generate",
    )

    # Product content
    description = RichTextField(help_text="Product description and details")
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Main product image",
    )

    # Product status
    in_stock = models.BooleanField(
        default=True, help_text="Whether the product is currently available"
    )
    featured = models.BooleanField(
        default=False, help_text="Show this product in featured sections"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    content_panels = Page.content_panels + [
        FieldPanel("sku"),
        FieldPanel("price"),
        FieldPanel("main_image"),
        FieldPanel("description"),
        InlinePanel("gallery_images", label="Gallery Images"),
        FieldPanel("in_stock"),
        FieldPanel("featured"),
    ]

    parent_page_types = ["shop.ShopCategoryPage"]
    subpage_types = []  # Products are leaf nodes

    search_fields = (
        Page.search_fields
        + [
            # Inherit Page.search_fields (title, etc.)
        ]
    )

    def get_category(self):
        """Returns the parent CategoryPage"""
        return self.get_parent().specific

    def save(self, *args, **kwargs):
        """Auto-generate SKU if not provided"""
        if not self.sku:
            # Generate SKU based on category and timestamp
            category = self.get_parent()
            if category:
                category_prefix = category.slug[:4].upper()
                # Use ID if available, otherwise use timestamp + random suffix
                if self.id:
                    self.sku = f"{category_prefix}-{self.id:04d}"
                else:
                    # For new products, use a timestamp-based SKU with random suffix
                    import random
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%m%d%H%M%S")
                    random_suffix = random.randint(1000, 9999)
                    self.sku = f"{category_prefix}-{timestamp}-{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
