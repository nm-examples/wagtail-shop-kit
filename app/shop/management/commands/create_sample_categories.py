import random

from django.core.management.base import BaseCommand
from wagtail.images.models import Image
from wagtail.models import Page

from app.shop.models import ShopCategoryPage, ShopIndexPage


class Command(BaseCommand):
    help = "Creates sample category pages for the shop under a ShopIndexPage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing ShopCategoryPage instances before creating new ones",
        )
        parser.add_argument(
            "--no-icons",
            action="store_true",
            help="Skip assigning icons to categories",
        )
        parser.add_argument(
            "--home-slug",
            type=str,
            default="home",
            help="Slug of the home page (default: home)",
        )
        parser.add_argument(
            "--shop-title",
            type=str,
            default="Shop",
            help="Title for the shop index page (default: Shop)",
        )
        parser.add_argument(
            "--shop-slug",
            type=str,
            default="shop",
            help="Slug for the shop index page (default: shop)",
        )

    def handle(self, *args, **options):
        # Find home page
        try:
            home_page = Page.objects.get(slug=options["home_slug"])
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Home page with slug '{options['home_slug']}' not found"
                )
            )
            return

        # Find or create ShopIndexPage
        shop_index = ShopIndexPage.objects.filter(slug=options["shop_slug"]).first()

        if shop_index:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found existing ShopIndexPage: '{shop_index.title}' at {shop_index.get_url()}"
                )
            )
        else:
            self.stdout.write("Creating ShopIndexPage...")
            shop_index = ShopIndexPage(
                title=options["shop_title"],
                slug=options["shop_slug"],
                intro="<p>Browse our collection of quality products across various categories.</p>",
                show_in_menus=True,
            )
            home_page.add_child(instance=shop_index)
            rev = shop_index.save_revision()
            rev.publish()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created ShopIndexPage: '{shop_index.title}' at {shop_index.get_url()}"
                )
            )

        # Reset if requested
        if options["reset"]:
            self.stdout.write("Deleting existing category pages...")
            all_categories = shop_index.get_children().type(ShopCategoryPage)
            deleted_count = all_categories.count()

            # Delete all at once instead of iterating
            for category in all_categories:
                category.delete()

            # Refresh shop index from database to update tree structure
            shop_index.refresh_from_db()

            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_count} category pages")
            )

        # Query available images (unless --no-icons is specified)
        available_images = []
        if not options["no_icons"]:
            available_images = list(Image.objects.all().order_by("?"))  # Random order
            if not available_images:
                self.stdout.write(
                    self.style.WARNING(
                        "No images found in database. Run 'python manage.py create_sample_media' first."
                    )
                )
                self.stdout.write(
                    self.style.WARNING("Creating categories without icons...")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(available_images)} images available for category icons"
                    )
                )

        # Category data matching the home page
        categories = [
            {
                "title": "Electronics",
                "slug": "electronics",
                "description": """
                    <p>Discover the latest gadgets and tech products. From smartphones and laptops to
                    smart home devices and wearables, find everything you need to stay connected and
                    productive in the digital age.</p>
                    <p>Our electronics collection features cutting-edge technology from leading brands,
                    ensuring quality and innovation in every product.</p>
                """,
                "featured": True,
            },
            {
                "title": "Fashion",
                "slug": "fashion",
                "description": """
                    <p>Explore our curated collection of clothing and accessories for every style and
                    occasion. From casual everyday wear to elegant formal attire, express your unique
                    personality through fashion.</p>
                    <p>We offer a diverse range of sizes, styles, and trends to suit everyone's taste.</p>
                """,
                "featured": True,
            },
            {
                "title": "Home & Living",
                "slug": "home-living",
                "description": """
                    <p>Transform your living space with our selection of furniture and decor. Create a
                    comfortable, stylish home that reflects your personality and meets your lifestyle needs.</p>
                    <p>From modern minimalist designs to classic traditional pieces, we have everything
                    to make your house a home.</p>
                """,
                "featured": True,
            },
            {
                "title": "Beauty",
                "slug": "beauty",
                "description": """
                    <p>Discover premium skincare and cosmetics to enhance your natural beauty. Our
                    carefully selected products help you look and feel your best every day.</p>
                    <p>From daily essentials to special occasion makeup, we offer quality beauty products
                    for all skin types and preferences.</p>
                """,
                "featured": False,
            },
            {
                "title": "Sports",
                "slug": "sports",
                "description": """
                    <p>Get active with our range of fitness and outdoor equipment. Whether you're a
                    seasoned athlete or just starting your fitness journey, we have the gear you need
                    to reach your goals.</p>
                    <p>Explore workout equipment, outdoor gear, and athletic wear designed for
                    performance and comfort.</p>
                """,
                "featured": False,
            },
            {
                "title": "Books",
                "slug": "books",
                "description": """
                    <p>Feed your mind with our diverse collection of books. From bestselling novels and
                    educational resources to inspiring biographies and practical guides, discover your
                    next great read.</p>
                    <p>We offer books across all genres and subjects, perfect for readers of all ages
                    and interests.</p>
                """,
                "featured": False,
            },
        ]

        created_count = 0

        # Shuffle images for random assignment
        if available_images:
            random.shuffle(available_images)

        for idx, category_data in enumerate(categories):
            # Check if category already exists under shop index
            existing = (
                shop_index.get_children()
                .type(ShopCategoryPage)
                .filter(slug=category_data["slug"])
                .first()
            )
            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f"Category '{category_data['title']}' already exists, skipping..."
                    )
                )
                continue

            # Create category page
            category_page = ShopCategoryPage(
                title=category_data["title"],
                slug=category_data["slug"],
                description=category_data["description"],
                featured=category_data["featured"],
                show_in_menus=True,  # Make categories appear in menus
            )

            # Assign icon from shuffled image list
            if available_images:
                # Use modulo to cycle through images if we have fewer images than categories
                icon_index = idx % len(available_images)
                category_page.icon = available_images[icon_index]
                self.stdout.write(
                    f"  Assigning icon: {category_page.icon.title} (ID: {category_page.icon.id})"
                )

            # Add as child of shop index page
            shop_index.add_child(instance=category_page)
            rev = category_page.save_revision()
            rev.publish()

            created_count += 1
            icon_status = (
                f" 🖼️  (icon: {category_page.icon.title[:30]}...)"
                if category_page.icon
                else " (no icon)"
            )
            featured_status = " ⭐ [FEATURED]" if category_page.featured else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ Created: {category_page.title}{icon_status}{featured_status}"
                )
            )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_count} category pages under '{shop_index.title}'"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("No new category pages were created"))

        # Display URLs
        if created_count > 0:
            self.stdout.write("\nCategory URLs:")
            for category in (
                shop_index.get_children()
                .type(ShopCategoryPage)
                .live()
                .order_by("title")
            ):
                self.stdout.write(f"  → {category.get_url()} - {category.title}")

        self.stdout.write("=" * 60)
