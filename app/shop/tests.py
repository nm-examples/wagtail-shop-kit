from decimal import Decimal

from django.test import TestCase
from wagtail.images.tests.utils import get_test_image_file
from wagtail.test.utils import WagtailPageTestCase

from app.home.models import HomePage
from app.shop.models import ProductImage, ProductPage, ShopCategoryPage, ShopIndexPage


class ShopIndexPageTest(WagtailPageTestCase):
    """Tests for ShopIndexPage model"""

    def setUp(self):
        self.home_page = HomePage.objects.first()

    def test_can_create_shop_index_page(self):
        """Test that ShopIndexPage can be created under HomePage"""
        self.assertCanCreateAt(HomePage, ShopIndexPage)

    def test_shop_index_page_only_allows_category_children(self):
        """Test that ShopIndexPage only allows ShopCategoryPage as children"""
        self.assertAllowedSubpageTypes(ShopIndexPage, {ShopCategoryPage})

    def test_shop_index_page_max_count(self):
        """Test that only one ShopIndexPage can be created"""
        # Create first shop index
        shop_index = ShopIndexPage(title="Shop", slug="shop", intro="<p>Test</p>")
        self.home_page.add_child(instance=shop_index)

        # Check max_count is enforced
        self.assertEqual(ShopIndexPage.max_count, 1)


class ShopCategoryPageTest(WagtailPageTestCase):
    """Tests for ShopCategoryPage model"""

    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.shop_index = ShopIndexPage(
            title="Shop", slug="shop", intro="<p>Browse our products</p>"
        )
        self.home_page.add_child(instance=self.shop_index)

    def test_can_create_category_page(self):
        """Test that ShopCategoryPage can be created under ShopIndexPage"""
        self.assertCanCreateAt(ShopIndexPage, ShopCategoryPage)

    def test_category_page_allows_product_children(self):
        """Test that ShopCategoryPage allows ProductPage as children"""
        self.assertAllowedSubpageTypes(ShopCategoryPage, {ProductPage})

    def test_category_page_creation(self):
        """Test creating a category page with all fields"""
        category = ShopCategoryPage(
            title="Electronics",
            slug="electronics",
            description="<p>Electronic products</p>",
            featured=True,
        )
        self.shop_index.add_child(instance=category)

        # Verify the category was created
        self.assertEqual(category.title, "Electronics")
        self.assertEqual(category.slug, "electronics")
        self.assertTrue(category.featured)

    def test_get_products_method(self):
        """Test that get_products() returns child ProductPage objects"""
        # Create category
        category = ShopCategoryPage(title="Electronics", slug="electronics")
        self.shop_index.add_child(instance=category)

        # Create some products
        for i in range(3):
            product = ProductPage(
                title=f"Product {i}",
                slug=f"product-{i}",
                price=Decimal("99.99"),
                description="<p>Test product</p>",
                sku=f"TEST-{i}",
            )
            category.add_child(instance=product)

        # Test get_products method
        products = category.get_products()
        self.assertEqual(products.count(), 3)


class ProductPageTest(WagtailPageTestCase):
    """Tests for ProductPage model"""

    def setUp(self):
        self.home_page = HomePage.objects.first()

        # Create shop structure
        self.shop_index = ShopIndexPage(title="Shop", slug="shop")
        self.home_page.add_child(instance=self.shop_index)

        self.category = ShopCategoryPage(
            title="Electronics",
            slug="electronics",
            description="<p>Electronic products</p>",
        )
        self.shop_index.add_child(instance=self.category)

    def test_can_create_product_page(self):
        """Test that ProductPage can be created under ShopCategoryPage"""
        self.assertCanCreateAt(ShopCategoryPage, ProductPage)

    def test_product_page_parent_types(self):
        """Test that ProductPage can only be created under ShopCategoryPage"""
        self.assertAllowedParentPageTypes(ProductPage, {ShopCategoryPage})

    def test_product_page_has_no_subpages(self):
        """Test that ProductPage is a leaf node (no subpages allowed)"""
        self.assertAllowedSubpageTypes(ProductPage, {})

    def test_product_page_creation_with_all_fields(self):
        """Test creating a product page with all required and optional fields"""
        product = ProductPage(
            title="Wireless Headphones",
            slug="wireless-headphones",
            price=Decimal("129.99"),
            sku="ELEC-001",
            description="<p>High quality wireless headphones</p>",
            in_stock=True,
            featured=True,
        )
        self.category.add_child(instance=product)

        # Verify all fields
        self.assertEqual(product.title, "Wireless Headphones")
        self.assertEqual(product.price, Decimal("129.99"))
        self.assertEqual(product.sku, "ELEC-001")
        self.assertTrue(product.in_stock)
        self.assertTrue(product.featured)
        self.assertIsNotNone(product.created_at)

    def test_product_sku_auto_generation(self):
        """Test that SKU is auto-generated when not provided"""
        product = ProductPage(
            title="Test Product",
            slug="test-product",
            price=Decimal("49.99"),
            description="<p>Test</p>",
        )
        self.category.add_child(instance=product)

        # SKU should be auto-generated
        self.assertIsNotNone(product.sku)
        self.assertTrue(product.sku.startswith("ELEC-"))

    def test_product_sku_uniqueness(self):
        """Test that SKU field enforces uniqueness"""
        # Create first product
        product1 = ProductPage(
            title="Product 1",
            slug="product-1",
            price=Decimal("99.99"),
            sku="TEST-123",
            description="<p>Test</p>",
        )
        self.category.add_child(instance=product1)

        # Try to create another product with same SKU
        product2 = ProductPage(
            title="Product 2",
            slug="product-2",
            price=Decimal("99.99"),
            sku="TEST-123",  # Same SKU
            description="<p>Test</p>",
        )

        # This should raise a validation error
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            self.category.add_child(instance=product2)

    def test_get_category_method(self):
        """Test that get_category() returns the parent category"""
        product = ProductPage(
            title="Test Product",
            slug="test-product",
            price=Decimal("99.99"),
            sku="TEST-001",
            description="<p>Test</p>",
        )
        self.category.add_child(instance=product)

        # Get category
        parent_category = product.get_category()
        self.assertEqual(parent_category.id, self.category.id)
        self.assertIsInstance(parent_category, ShopCategoryPage)

    def test_product_page_str_method(self):
        """Test the string representation of ProductPage"""
        product = ProductPage(
            title="Test Product",
            slug="test-product",
            price=Decimal("99.99"),
            sku="TEST-001",
            description="<p>Test</p>",
        )
        self.category.add_child(instance=product)

        self.assertEqual(str(product), "Test Product")


class ProductImageTest(TestCase):
    """Tests for ProductImage inline model"""

    def setUp(self):
        from wagtail.images.models import Image

        self.home_page = HomePage.objects.first()

        # Create shop structure
        self.shop_index = ShopIndexPage(title="Shop", slug="shop")
        self.home_page.add_child(instance=self.shop_index)

        self.category = ShopCategoryPage(title="Electronics", slug="electronics")
        self.shop_index.add_child(instance=self.category)

        self.product = ProductPage(
            title="Test Product",
            slug="test-product",
            price=Decimal("99.99"),
            sku="TEST-001",
            description="<p>Test</p>",
        )
        self.category.add_child(instance=self.product)

        # Create test image
        self.image = Image.objects.create(
            title="Test image", file=get_test_image_file()
        )

    def test_product_image_creation(self):
        """Test creating a ProductImage"""
        product_image = ProductImage.objects.create(
            product=self.product, image=self.image, caption="Test caption"
        )

        self.assertEqual(product_image.product, self.product)
        self.assertEqual(product_image.image, self.image)
        self.assertEqual(product_image.caption, "Test caption")

    def test_product_image_gallery_relationship(self):
        """Test that product images are accessible via gallery_images"""
        # Create multiple gallery images
        for i in range(3):
            ProductImage.objects.create(
                product=self.product,
                image=self.image,
                caption=f"Gallery image {i}",
                sort_order=i,
            )

        # Check that all images are accessible
        gallery_images = self.product.gallery_images.all()
        self.assertEqual(gallery_images.count(), 3)

    def test_product_image_ordering(self):
        """Test that product images are ordered by sort_order"""
        # Create images with specific sort orders
        ProductImage.objects.create(
            product=self.product, image=self.image, caption="Third", sort_order=3
        )
        ProductImage.objects.create(
            product=self.product, image=self.image, caption="First", sort_order=1
        )
        ProductImage.objects.create(
            product=self.product, image=self.image, caption="Second", sort_order=2
        )

        # Get ordered images
        ordered_images = self.product.gallery_images.all()
        self.assertEqual(ordered_images[0].caption, "First")
        self.assertEqual(ordered_images[1].caption, "Second")
        self.assertEqual(ordered_images[2].caption, "Third")

    def test_product_image_str_method(self):
        """Test the string representation of ProductImage"""
        product_image = ProductImage.objects.create(
            product=self.product, image=self.image, caption="Test"
        )

        self.assertEqual(str(product_image), "Image for Test Product")


class ProductPageTemplateTest(TestCase):
    """Tests for ProductPage template rendering"""

    def setUp(self):
        self.home_page = HomePage.objects.first()

        # Create shop structure
        self.shop_index = ShopIndexPage(title="Shop", slug="shop")
        self.home_page.add_child(instance=self.shop_index)

        self.category = ShopCategoryPage(title="Electronics", slug="electronics")
        self.shop_index.add_child(instance=self.category)

        self.product = ProductPage(
            title="Test Product",
            slug="test-product",
            price=Decimal("99.99"),
            sku="TEST-001",
            description="<p>This is a test product</p>",
            in_stock=True,
        )
        self.category.add_child(instance=self.product)

        # Publish the pages
        revision = self.product.save_revision()
        revision.publish()

    def test_product_page_renders(self):
        """Test that product page returns 200 status"""
        response = self.client.get(self.product.url)
        self.assertEqual(response.status_code, 200)

    def test_product_page_uses_correct_template(self):
        """Test that product page uses the correct template"""
        response = self.client.get(self.product.url)
        self.assertTemplateUsed(response, "shop/product_page.html")

    def test_product_page_context(self):
        """Test that product page has correct context"""
        response = self.client.get(self.product.url)

        # Check that page object is in context
        self.assertEqual(response.context["page"], self.product)
        self.assertIn("Test Product", response.content.decode())
        self.assertIn("$99.99", response.content.decode())
        self.assertIn("In Stock", response.content.decode())
