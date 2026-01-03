import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker
from wagtail.images.models import Image
from wagtail.models import Page

from app.shop.models import ProductImage, ProductPage, ShopCategoryPage

fake = Faker()


class Command(BaseCommand):
    help = "Creates sample product pages for testing under existing category pages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of products to create per category (default: 20)",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing ProductPage instances before creating new ones",
        )
        parser.add_argument(
            "--with-images",
            action="store_true",
            help="Generate sample product images and gallery",
        )
        parser.add_argument(
            "--featured",
            type=int,
            default=3,
            help="Number of products per category to mark as featured (default: 3)",
        )

    def handle(self, *args, **options):
        # Fix tree structure first (in case it's corrupted)
        self.stdout.write("Fixing page tree structure...")
        Page.fix_tree()

        # Get all category pages
        categories = ShopCategoryPage.objects.live()

        if not categories.exists():
            self.stdout.write(
                self.style.ERROR(
                    "No category pages found. Run 'python manage.py create_sample_categories' first."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {categories.count()} category pages")
        )

        # Reset if requested
        if options["reset"]:
            self.stdout.write("Deleting existing product pages...")
            all_products = ProductPage.objects.all()
            deleted_count = all_products.count()
            all_products.delete()

            # Refresh all categories from database to update tree structure
            for category in categories:
                category.refresh_from_db()

            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_count} product pages")
            )

        # Get available images for products
        available_images = []
        if options["with_images"]:
            available_images = list(Image.objects.all().order_by("?"))  # Random order
            if not available_images:
                self.stdout.write(
                    self.style.WARNING(
                        "No images found in database. Run 'python manage.py create_sample_media' first."
                    )
                )
                self.stdout.write(
                    self.style.WARNING("Creating products without images...")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(available_images)} images available for products"
                    )
                )

        # Product name templates by category
        product_templates = {
            "electronics": [
                "Wireless Bluetooth Headphones",
                "Smart Watch Series {n}",
                "Portable Bluetooth Speaker",
                "USB-C Fast Charger",
                "Wireless Mouse",
                "Mechanical Keyboard",
                "HD Webcam",
                "Laptop Stand",
                "Phone Case",
                "Screen Protector",
                "Power Bank 20000mAh",
                "Wireless Earbuds",
                "HDMI Cable",
                "Gaming Controller",
                "LED Desk Lamp",
            ],
            "fashion": [
                "Cotton T-Shirt",
                "Denim Jeans",
                "Leather Jacket",
                "Running Shoes",
                "Canvas Sneakers",
                "Wool Sweater",
                "Summer Dress",
                "Casual Shorts",
                "Baseball Cap",
                "Leather Belt",
                "Cotton Socks (3-Pack)",
                "Winter Coat",
                "Scarf",
                "Gloves",
                "Sunglasses",
            ],
            "home-living": [
                "Ceramic Coffee Mug",
                "Throw Pillow",
                "Floor Lamp",
                "Wall Clock",
                "Photo Frame",
                "Desk Organizer",
                "Storage Box",
                "Area Rug",
                "Curtain Panel",
                "Table Lamp",
                "Decorative Vase",
                "Wall Art Print",
                "Couch Cover",
                "Bedding Set",
                "Kitchen Mat",
            ],
            "beauty": [
                "Facial Cleanser",
                "Moisturizing Cream",
                "Lip Balm",
                "Face Mask Set",
                "Makeup Brush Set",
                "Eyeshadow Palette",
                "Liquid Foundation",
                "Hair Serum",
                "Nail Polish Set",
                "Body Lotion",
                "Sunscreen SPF 50",
                "Anti-Aging Serum",
                "Exfoliating Scrub",
                "Makeup Remover",
                "Hair Straightener",
            ],
            "sports": [
                "Yoga Mat",
                "Resistance Bands Set",
                "Dumbbell Set",
                "Water Bottle",
                "Running Shorts",
                "Sports Bra",
                "Fitness Tracker",
                "Jump Rope",
                "Gym Bag",
                "Foam Roller",
                "Athletic Socks",
                "Compression Sleeves",
                "Exercise Ball",
                "Knee Support",
                "Sweat Towel",
            ],
            "books": [
                "The Art of Programming",
                "Mystery Novel Collection",
                "Cookbook: Healthy Recipes",
                "Self-Help Guide",
                "Science Fiction Novel",
                "Biography: Inspiring Lives",
                "Children's Story Book",
                "Travel Guide",
                "Business Strategy Book",
                "Poetry Collection",
                "History Encyclopedia",
                "Graphic Novel",
                "Language Learning Book",
                "Philosophy Reader",
                "DIY Home Improvement",
            ],
        }

        total_created = 0
        total_images_created = 0

        for category in categories:
            self.stdout.write(f"\nProcessing category: {category.title}")
            self.stdout.write("-" * 60)

            # Get product templates for this category
            category_slug = category.slug
            templates = product_templates.get(
                category_slug, ["Product {n}"] * options["count"]
            )

            # Ensure we have enough product names
            if len(templates) < options["count"]:
                # Cycle through templates if we need more
                templates = templates * ((options["count"] // len(templates)) + 1)

            # Shuffle templates for variety
            random.shuffle(templates)

            for i in range(options["count"]):
                # Generate product title
                product_title = templates[i].format(n=i + 1)

                # Check if product already exists
                existing = (
                    category.get_children()
                    .type(ProductPage)
                    .filter(title=product_title)
                )
                if existing.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Product '{product_title}' already exists, skipping..."
                        )
                    )
                    continue

                # Generate realistic price (10-500 range with .99 endings)
                price_base = random.randint(10, 500)
                price = Decimal(f"{price_base}.99")

                # Generate rich text description
                description = self._generate_description(product_title, category.title)

                # Random stock status (80% in stock)
                in_stock = random.random() < 0.8

                # Determine if featured (first N products per category)
                featured = i < options["featured"]

                # Generate SKU with category prefix and random suffix
                from datetime import datetime

                category_prefix = category.slug[:4].upper()
                timestamp = datetime.now().strftime("%m%d%H%M%S%f")[
                    :14
                ]  # Include microseconds
                sku = f"{category_prefix}-{timestamp}"

                # Create product page
                product = ProductPage(
                    title=product_title,
                    price=price,
                    sku=sku,  # Explicitly set SKU
                    description=description,
                    in_stock=in_stock,
                    featured=featured,
                    show_in_menus=False,
                )

                # Assign main image if available
                if available_images:
                    product.main_image = random.choice(available_images)

                # Add as child of category
                category.add_child(instance=product)
                rev = product.save_revision()
                rev.publish()

                # Add gallery images (2-4 images per product)
                if available_images and options["with_images"]:
                    num_gallery_images = random.randint(2, 4)
                    # Get random images, ensuring no duplicates
                    gallery_images = random.sample(
                        available_images, min(num_gallery_images, len(available_images))
                    )

                    for img in gallery_images:
                        ProductImage.objects.create(
                            product=product,
                            image=img,
                            caption=f"{product_title} - {fake.sentence(nb_words=4)}",
                            sort_order=gallery_images.index(img),
                        )
                        total_images_created += 1

                total_created += 1

                # Status indicators
                status_indicators = []
                if product.main_image:
                    status_indicators.append("🖼️ ")
                if product.featured:
                    status_indicators.append("⭐")
                if not product.in_stock:
                    status_indicators.append("📦")

                status = " ".join(status_indicators)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {product.title} - ${product.price} {status}"
                    )
                )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {total_created} product pages across {categories.count()} categories"
            )
        )
        if options["with_images"] and total_images_created > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Added {total_images_created} gallery images to products"
                )
            )

        self.stdout.write("\nLegend:")
        self.stdout.write("  🖼️  = Has main image")
        self.stdout.write("  ⭐ = Featured product")
        self.stdout.write("  📦 = Out of stock")
        self.stdout.write("=" * 60)

    def _generate_description(self, product_title, category_title):
        """Generate realistic product description using Faker"""
        intro = fake.paragraph(nb_sentences=2)
        features = "\n".join(
            [f"<li>{fake.sentence()}</li>" for _ in range(random.randint(3, 5))]
        )
        closing = fake.paragraph(nb_sentences=1)

        return f"""
            <p>{intro}</p>
            <h3>Key Features:</h3>
            <ul>
                {features}
            </ul>
            <p>{closing}</p>
        """
