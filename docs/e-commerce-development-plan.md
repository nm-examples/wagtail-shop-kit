# Wagtail Shop Kit - E-commerce Development Plan

## Overview

Incremental development plan for building out e-commerce functionality in Wagtail Shop Kit. This plan focuses on establishing the content foundation (categories, products, pages) before adding transactional features (cart, checkout, users).

## Development Philosophy

- **Start with foundation**: Categories → Products → Listings
- **Content before transactions**: Build browsable catalog before cart/checkout
- **Wagtail-native patterns**: Use Pages for URLs, Snippets for reusable content
- **Test as you go**: Write tests for each phase
- **Keep it simple**: Start with MVP features, iterate later
- **Reproducible content**: Create management commands and/or fixtures for each phase to enable UI testing and quick site resets

---

## Data Management & Fixtures Strategy

**Goal**: Every phase should produce reproducible sample data for testing and development.

### Approach

For each phase of development:

1. **Management Commands** (Preferred for complex data):
   - Create command in `app/shop/management/commands/`
   - Follow pattern from existing `create_sample_media.py`
   - Generate realistic sample data with randomization
   - Support options: `--count`, `--reset`, `--clear`
   - Make idempotent (safe to run multiple times)
   - Log progress clearly

2. **Fixtures** (For simple, static data):
   - Create JSON fixtures in `app/shop/fixtures/`
   - Use for consistent reference data (categories, sample users)
   - Load with `python manage.py loaddata <fixture_name>`
   - Keep minimal and focused

### Benefits

- **UI Testing**: Quickly populate site with realistic content for visual testing
- **Demo Environments**: Spin up demo sites with full content in seconds
- **Onboarding**: New developers can see working examples immediately
- **CI/CD**: Automated testing with predictable data
- **Site Resets**: Recover from mistakes or experiments quickly

### Naming Convention

Management commands should follow this pattern:
- Phase 1: `setup_phase1_categories.py` or `create_sample_categories.py`
- Phase 2: `setup_phase2_products.py` or `create_sample_products.py`
- Phase 3: `setup_phase3_category_pages.py`
- Phase 4: `setup_phase4_product_index.py`
- Or create cumulative: `setup_shop_demo.py --phase=1` to `--phase=6`

### Quick Setup Workflow

After implementing each phase:
```bash
# Reset database
make down && make up && make migrate

# Create superuser
make superuser

# Run phase setup commands
python manage.py setup_phase1_categories
python manage.py setup_phase2_products --count=50
python manage.py setup_phase3_category_pages
python manage.py setup_phase4_product_index

# Or use all-in-one command
python manage.py setup_shop_demo --all-phases
```

---

## Phase 1: Category Pages

**Goal**: Create category pages as the foundation of the page tree hierarchy

### Architecture Decision

Categories are implemented as **Wagtail Pages** (not snippets) to leverage Wagtail's page tree for hierarchical navigation. Products will be children of category pages, creating a natural URL structure like `/electronics/wireless-headphones/`.

**Trade-offs:**
- ✅ Natural URL hierarchy and breadcrumbs
- ✅ Built-in Wagtail admin page management
- ✅ Easy to add category-specific content and templates
- ⚠️ Products can only belong to one category (parent page relationship)
- ⚠️ Moving products between categories requires page tree operations

### Tasks

1. **Create shop app**
   ```bash
   python manage.py startapp shop
   ```
   - Add to `INSTALLED_APPS` in `app/settings/base.py`
   - Create `app/shop/templates/shop/` directory structure
   - Create initial `__init__.py`, `models.py`, `admin.py`, `tests.py`

2. **Create CategoryPage model**
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

3. **Create category page template**
   - File: `app/shop/templates/shop/category_page.html`
   - Extends: `base.html`
   - Sections:
     - Category header (title, description, icon)
     - Child categories (if any)
     - Product grid showing child products
     - Pagination
   - Responsive design using Pico CSS

4. **Run migrations**
   ```bash
   python manage.py makemigrations shop
   python manage.py migrate
   ```

5. **Create sample categories command**
   - **Management command**: `create_sample_categories.py`
   - Creates 6 category pages as children of HomePage:
     - Electronics, Fashion, Home & Living, Beauty, Sports, Books
   - Options:
     - `--reset`: Delete existing category pages
     - `--with-icons`: Create icon images
     - `--parent-slug=home`: Specify parent page (default: HomePage)
   - **Purpose**: Reproducible category page structure for demos

6. **Write tests**
   - File: `app/shop/tests.py`
   - Test CategoryPage creation and page tree hierarchy
   - Test get_products() method
   - Test category page rendering
   - Test admin page operations (create, edit, move)

**Deliverable**: CategoryPage model working in Wagtail page tree, ready to contain products

---

## Phase 2: Product Detail Pages

**Goal**: Create individual product pages as children of categories

### Tasks

1. **Create ProductPage model**
   - File: `app/shop/models.py`
   - Extends: `wagtail.models.Page`
   - Fields:
     - `price` (DecimalField, max_digits=10, decimal_places=2)
     - `sku` (CharField, unique, optional, help_text for auto-generation)
     - `description` (RichTextField)
     - `main_image` (ForeignKey to wagtailimages.Image)
     - `in_stock` (BooleanField, default=True)
     - `featured` (BooleanField, default=False)
     - `created_at` (DateTimeField, auto_now_add=True)
   - Content panels:
     - Basic info: title, sku, price
     - Content: description (rich text), main_image
     - Settings: in_stock, featured
   - Parent page types: `CategoryPage` (products must be under a category)
   - Subpage types: None (leaf node)
   - Search fields: title, description, sku
   - Methods:
     - `get_category()`: Returns parent CategoryPage
     - `save()`: Auto-generate SKU if not provided

2. **Create product detail template**
   - File: `app/shop/templates/shop/product_page.html`
   - Extends: `base.html`
   - Sections:
     - Product image (large, responsive)
     - Product title and category breadcrumb
     - Price display (prominent, styled)
     - Description (rich text)
     - Stock status indicator
     - "Add to Cart" placeholder button (non-functional for now)
     - Related products section (future)
   - Styling in `{% block extra_css %}` using Pico CSS

3. **Enhance ProductPage with image gallery**
   - Create `ProductImage` model (inline):
     - ForeignKey to ProductPage (ParentalKey for Wagtail)
     - ForeignKey to wagtailimages.Image
     - `caption` (CharField, optional)
     - `display_order` (IntegerField)
   - Use `InlinePanel` in ProductPage
   - Add gallery to template (thumbnail strip + lightbox)

4. **Run migrations**
   ```bash
   python manage.py makemigrations shop
   python manage.py migrate
   ```

5. **Create sample products command**
   - **Management command**: `create_sample_products.py`
   - **Required for UI testing**: Generate realistic browsable products
   - Options:
     - `--count=20`: Number of products per category (default: 20)
     - `--with-images`: Generate sample product images
     - `--reset`: Clear existing product pages first
     - `--featured=5`: Mark N products per category as featured
   - Generate realistic product data using Faker:
     - Product names (e.g., "Wireless Bluetooth Speaker", "Cotton T-Shirt")
     - Rich text descriptions (2-3 paragraphs)
     - Prices: $10-$500 range with .99 endings
     - SKUs: Auto-generated (e.g., "ELEC-001", "FASH-042")
     - Random in_stock status (80% in stock)
   - Create products as children of CategoryPage instances
   - Distribute evenly across all existing categories
   - Generate 2-4 images per product using `create_sample_media` pattern
   - **Purpose**: Reproducible product catalog for testing all product features

6. **Write tests**
   - Test ProductPage creation with all fields
   - Test image gallery inline
   - Test get_category() method returns parent
   - Test parent page type restriction (must be CategoryPage)
   - Test template rendering (200 status)
   - Test search indexing
   - Test SKU auto-generation

**Deliverable**: Individual product pages with images, descriptions, browsable via Wagtail page tree under categories

---

## Phase 3: Product Listing/Shop Index Page

**Goal**: Create a main shop page showing all products with filtering

### Architecture Note

Since products are organized under CategoryPages in the tree, we need a separate page type that can list and filter products from across all categories. This provides a "browse all products" view independent of the category hierarchy.

### Tasks

1. **Create ProductIndexPage model**
   - File: `app/shop/models.py`
   - Extends: `wagtail.models.Page`
   - Fields:
     - `intro` (RichTextField, blank=True)
     - `products_per_page` (IntegerField, default=12)
     - `show_filters` (BooleanField, default=True)
   - Content panels:
     - Basic: title, intro, products_per_page, show_filters
   - Parent page types: `HomePage`
   - Subpage types: None (leaf node)
   - Max count: 1 (only one shop index)
   - Methods:
     - `get_products()`: Returns all ProductPage objects (live, ordered)
     - `get_categories()`: Returns all CategoryPage objects for filter sidebar
     - `get_context()`: Add products, categories, filters, pagination to template

2. **Add filtering functionality to ProductIndexPage**
   - Handle GET parameters in `get_context()`:
     - `category`: Filter by CategoryPage slug
     - `min_price`, `max_price`: Price range
     - `in_stock`: Show only available
     - `featured`: Show featured products
     - `sort`: Order by (price_asc, price_desc, newest, name)
   - Add pagination support (Django Paginator)

3. **Create product index template**
   - File: `app/shop/templates/shop/product_index_page.html`
   - Extends: `base.html`
   - Sections:
     - Page intro/description
     - Filter sidebar/panel:
       - Category filter (links to CategoryPages)
       - Price range sliders
       - In stock toggle
       - Featured toggle
       - Sort dropdown
     - Product grid (same styling as category page)
     - Result count ("Showing X of Y products")
     - Pagination controls
   - Responsive: Filters collapse to dropdown on mobile

4. **Integrate with search**
   - Update `app/search/views.py`:
     - Filter results to show ProductPages
     - Add product-specific result template
   - Add search box to header navigation
   - Link from ProductIndexPage

5. **Update navigation**
   - Update `app/home/templates/home/welcome_page.html`:
     - Link "Shop Now" CTA to ProductIndexPage
     - Link category cards to CategoryPage URLs
   - Add "Shop" link to header navigation pointing to ProductIndexPage

6. **Run migrations**
   ```bash
   python manage.py makemigrations shop
   python manage.py migrate
   ```

7. **Create product index page** (via admin or command)
   - **Optional management command**: `setup_product_index.py`
   - Create ProductIndexPage under HomePage programmatically
   - Slug: `/shop/` or `/products/`
   - Set intro text, products_per_page, show_filters
   - **Alternative**: Document manual creation via Wagtail admin
   - **Purpose**: Quick setup of main shop entry point

8. **Write tests**
   - Test ProductIndexPage creation
   - Test get_products() returns all products
   - Test get_categories() returns all categories
   - Test filtering by category, price, stock
   - Test sorting options
   - Test pagination
   - Test search integration
   - Test template rendering

**Deliverable**: Main shop page with all products, filtering, sorting, and search

---

## Phase 4: Product Enhancements

**Goal**: Create a page showing all products with filtering and search

### Tasks

1. **Create ProductIndexPage model**
   - File: `app/shop/models.py`
   - Extends: `wagtail.models.Page`
   - Fields:
     - `intro` (RichTextField, optional)
     - `products_per_page` (IntegerField, default=12)
     - `show_filters` (BooleanField, default=True)
   - Methods:
     - `get_products()`: Returns all ProductPages
     - `get_context()`: Add products, categories, filters to context
   - Max count: 1 (only one shop index page)
   - Parent page types: HomePage
   - Subpage types: ProductPage (can create products under it)

2. **Add filtering functionality**
   - Update `get_context()` to handle GET parameters:
     - `category`: Filter by category ID/slug
     - `min_price`, `max_price`: Price range
     - `in_stock`: Show only available
     - `featured`: Show featured products
     - `sort`: Order by (price_asc, price_desc, newest, name)
   - Add pagination

3. **Create product index template**
   - File: `app/shop/templates/shop/product_index_page.html`
   - Extends: `base.html`
   - Sections:
     - Page intro/description
     - Filter sidebar/panel:
       - Category checkboxes
       - Price range sliders
       - In stock toggle
       - Featured toggle
       - Sort dropdown
     - Product grid (same styling as category page)
     - Pagination
     - Result count ("Showing X of Y products")
   - Responsive: Filters collapse to dropdown on mobile

4. **Integrate with search**
   - Update `app/search/views.py`:
     - Filter results to show ProductPages
     - Add product-specific result template
   - Add search box to header navigation
   - Consider: Autocomplete/suggestions (future enhancement)

5. **Run migrations**
   ```bash
   python manage.py makemigrations shop
   python manage.py migrate
   ```

6. **Create product index page command**
   - **Management command**: `setup_product_index.py` (optional)
   - Create ProductIndexPage under HomePage programmatically
   - Slug: `/shop/` or `/products/`
   - Set intro text, products_per_page, show_filters
   - **Alternative**: Document manual creation via Wagtail admin
   - **Purpose**: Reproducible main shop page for testing filtering/search

7. **Write tests**
   - Test ProductIndexPage creation
   - Test filtering by category, price, stock
   - Test sorting
   - Test pagination
   - Test search integration
   - Test template rendering

**Deliverable**: Main shop page with all products, filtering, sorting, and search

---

## Phase 5: Product Enhancements

**Goal**: Add features to make products more appealing and useful

### Tasks

1. **Add product variants**
   - Create `ProductVariant` model:
     - ParentalKey to ProductPage
     - `name` (CharField: "Small", "Red", etc.)
     - `variant_type` (CharField: "Size", "Color")
     - `price_modifier` (DecimalField, can be positive/negative)
     - `sku_suffix` (CharField)
     - `in_stock` (BooleanField)
   - Add InlinePanel to ProductPage
   - Update template to show variant selector
   - JavaScript for variant selection (update price display)

2. **Add product specifications**
   - Use StreamField or TableBlock for specifications:
     - Option A: RichTextField with table block
     - Option B: JSONField with structured data
     - Option C: StructBlock in StreamField
   - Display as formatted table in template
   - Examples: Dimensions, Weight, Materials, Care Instructions

3. **Add related products**
   - Add `related_products` field to ProductPage:
     - ParentalManyToManyField to ProductPage
   - Display in product detail template
   - Show 3-4 related product cards
   - Auto-suggest: Same category products (fallback if none manually selected)

4. **Add product reviews (simple version)**
   - Create `ProductReview` snippet:
     - ForeignKey to ProductPage
     - `author_name` (CharField)
     - `rating` (IntegerField, 1-5)
     - `comment` (TextField)
     - `created_at` (DateTimeField)
     - `is_approved` (BooleanField, default=False)
   - Display approved reviews on product page
   - Show average rating
   - Add simple review submission form (no auth required yet)

5. **Add breadcrumbs**
   - Create breadcrumb template tag or include
   - Show: Home > Category > Product
   - Add to all shop templates

6. **Optimize images**
   - Create image renditions for common sizes:
     - Thumbnail: 200x200
     - Product card: 400x400
     - Product detail: 800x800
   - Update templates to use renditions
   - Consider: WebP format for better performance

7. **Create sample variants, reviews, and related products**
   - **Management command**: `enhance_sample_products.py`
   - Add variants to existing products:
     - Sizes for clothing (S, M, L, XL)
     - Colors for applicable products
     - Price modifiers (+$5 for Large, etc.)
   - Generate sample reviews using Faker:
     - 3-5 reviews per product
     - Ratings 3-5 stars (weighted toward higher)
     - Realistic review text
     - Mix of approved/unapproved
   - Link related products:
     - Same category products
     - 3-4 related per product
   - Options:
     - `--variants-only`
     - `--reviews-only`
     - `--related-only`
     - `--reset`
   - **Purpose**: Reproducible enhanced product data for full feature testing

8. **Run migrations**
   ```bash
   python manage.py makemigrations shop
   python manage.py migrate
   ```

9. **Write tests**
   - Test variants creation and display
   - Test specifications rendering
   - Test related products logic
   - Test review submission and approval
   - Test breadcrumbs generation

**Deliverable**: Enhanced product pages with variants, specs, reviews, and related products

---

## Phase 6: Supporting Content Pages

**Goal**: Create standard e-commerce pages for information and support

### Tasks

1. **Create StandardPage model** (if not exists)
   - File: `app/shop/models.py` or new `app/content/models.py`
   - Extends: `wagtail.models.Page`
   - Fields:
     - `body` (StreamField with rich text, images, headings)
   - Parent: HomePage
   - Use for: About, Contact, FAQ, Shipping Info, Returns Policy

2. **Create specific pages**
   - About Us page: Company story, mission
   - Contact page: Form with email submission
   - FAQ page: Accordion-style questions
   - Shipping & Returns: Policy details
   - Terms & Conditions: Legal text
   - Privacy Policy: GDPR compliance

3. **Update footer links**
   - File: `app/home/templates/home/welcome_page.html`
   - Link footer sections to actual pages:
     - Customer Support → FAQ, Contact
     - Shop → ProductIndexPage, Categories
     - Account → Login (placeholder for Phase 7+)

4. **Create contact form**
   - Use `wagtail.contrib.forms`:
     - Create ContactFormPage model
     - Fields: name, email, subject, message
     - Email notification on submission
   - Template with styled form
   - Success message after submission

5. **Create sample content pages command**
   - **Management command**: `create_content_pages.py`
   - Create standard pages:
     - About Us (with rich text content)
     - FAQ (with questions and answers)
     - Shipping & Returns (policy text)
     - Terms & Conditions
     - Privacy Policy
   - Create ContactFormPage under HomePage
   - Options:
     - `--reset`: Delete existing content pages
     - `--pages=about,faq`: Create specific pages only
   - **Purpose**: Reproducible informational pages for complete site testing

6. **Write tests**
   - Test StandardPage creation
   - Test contact form submission
   - Test email sending (use Django test email backend)

**Deliverable**: Complete informational pages linked from footer, contact form functional

---

## Phase 7+: Future Enhancements (Not in Current Scope)

These will be planned separately after core shop functionality is complete:

### User Management & Authentication
- User registration and login
- User profiles
- Order history
- Wishlist
- Saved addresses

### Shopping Cart
- Add to cart functionality
- Cart page with item list
- Update quantities
- Remove items
- Cart persistence (session/database)

### Checkout Process
- Shipping address form
- Billing address form
- Shipping method selection
- Payment integration (Stripe, PayPal)
- Order confirmation page
- Order confirmation emails

### Order Management
- Order model
- Order items model
- Order status tracking
- Admin order management
- Customer order history

### Advanced Features
- Inventory management
- Product stock alerts
- Discount codes/coupons
- Gift cards
- Product recommendations (ML)
- Analytics integration

---

## Technical Guidelines

### Wagtail Best Practices

1. **Use Snippets for reusable content**: Categories, variants, shipping methods
2. **Use Pages for browsable content**: Products, categories, listings
3. **Use StreamFields for flexible content**: Product descriptions, page bodies
4. **Add search_fields to all Page models**: Improve search functionality
5. **Use ParentalKey for inline relationships**: Images, variants
6. **Test admin access**: Ensure all models editable via Wagtail admin

### Documentation References

When implementing Wagtail features, refer to the official documentation:

**Wagtail CMS Documentation**: https://docs.wagtail.org/en/stable/

Particularly relevant sections for e-commerce development:
- [Page Models & Fields](https://docs.wagtail.org/en/stable/topics/pages.html) - Creating ProductPage, CategoryPage, etc.
- [Snippets](https://docs.wagtail.org/en/stable/topics/snippets.html) - ProductCategory, ProductVariant snippets
- [Images & Renditions](https://docs.wagtail.org/en/stable/topics/images.html) - Product image handling
- [Search](https://docs.wagtail.org/en/stable/topics/search/index.html) - Product search functionality
- [Forms](https://docs.wagtail.org/en/stable/reference/contrib/forms.html) - Contact form implementation
- [Testing](https://docs.wagtail.org/en/stable/advanced_topics/testing.html) - Writing tests for page types

**Django Documentation**: https://docs.djangoproject.com/en/5.2/

### Database Considerations

- Start with PostgreSQL or MySQL (not SQLite) for production readiness
- Add indexes to frequently queried fields: category, price, sku
- Use select_related/prefetch_related for efficient queries
- Consider: Database views for complex product filtering

### Frontend Guidelines

- Reuse home page product card styling for consistency
- Keep extra_css in templates for page-specific styles
- Use Pico CSS variables: `--pico-primary`, `--pico-muted-color`
- Ensure responsive design at 768px, 1024px, 1280px breakpoints
- Optimize images: Use Wagtail renditions, serve WebP where supported

### Testing Strategy

- Test model creation and relationships
- Test page rendering (200 status codes)
- Test Wagtail admin CRUD operations
- Test filtering and search functionality
- Test template context variables
- Run tests after each phase: `make test`

### Migration Management

- Create migrations after each model change
- Test migrations on fresh database
- Document any data migrations needed
- Keep migrations small and focused

### Management Commands & Fixtures

**Management Commands** (for complex, randomized data):
- Follow pattern in `create_sample_media.py`
- **Must create for each phase** to generate sample content
- Add `--help` text for all options
- Support options:
  - `--count=N`: Number of items to create
  - `--reset`: Clear existing data first
  - `--clear`: Delete all data without creating new
  - `--phase=N`: For cumulative setup commands
- Support idempotent operations (safe to run multiple times)
- Log progress and success messages with clear output
- Use Faker library for realistic data (names, descriptions, prices)

**Fixtures** (for static reference data):
- Create JSON fixtures in `app/shop/fixtures/`
- Use `python manage.py dumpdata` to create from existing data
- Load with `python manage.py loaddata <fixture_name>`
- Good for: Categories, sample users, consistent test data
- Version control fixtures for reproducibility

**Example Command Structure**:
```python
# app/shop/management/commands/create_sample_products.py
from django.core.management.base import BaseCommand
from faker import Faker
from app.shop.models import ProductPage, ProductCategory
from app.home.models import HomePage

class Command(BaseCommand):
    help = "Create sample products for testing"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20)
        parser.add_argument('--reset', action='store_true')
        parser.add_argument('--clear', action='store_true')

    def handle(self, *args, **options):
        # Implementation
        pass
```

**Why This Matters**:
- Enables quick UI testing after each development phase
- Allows easy site resets during development
- Provides realistic demo content for stakeholders
- Speeds up onboarding for new developers
- Makes CI/CD testing more reliable

---

## Success Criteria by Phase

### Phase 1 ✓
- CategoryPage model created and working
- Category pages browsable in Wagtail page tree
- Category template displays products and subcategories
- Sample categories created via management command
- Tests passing

### Phase 2 ✓
- Individual products browsable via Wagtail tree
- Product detail pages render with images
- Sample products created
- Management command creates realistic product catalog
- Tests passing

### Phase 3 ✓
- Category pages show filtered products
- Category links work from home page
- Pagination functional
- Management command creates all category pages
- Tests passing

### Phase 4 ✓
- Product index page shows all products
- Filtering by category, price, stock works
- Search returns product results
- Sort options functional
- Product index page setup is reproducible
- Tests passing

### Phase 5 ✓
- Product variants selectable
- Specifications display in tables
- Related products show
- Reviews submission works
- Breadcrumbs appear
- Management command enhances products with variants/reviews
- Tests passing

### Phase 6 ✓
- All info pages created and linked
- Contact form submits successfully
- Footer links functional
- Management command creates all content pages
- Tests passing

---

## Implementation Order Summary

```
1. CategoryPage (page) ← Foundation - categories as pages in tree
2. ProductPage (page) ← Core content - products as children of categories
3. ProductIndexPage (page) ← Browse all products with filtering
4. ProductVariant, ProductImage (inlines) ← Product enhancements
5. ProductReview (snippet) ← Social proof
6. StandardPage, ContactFormPage (pages) ← Supporting content
```

**Page Tree Structure:**
```
HomePage
├── CategoryPage (Electronics)
│   ├── ProductPage (Wireless Headphones)
│   ├── ProductPage (Bluetooth Speaker)
│   └── ...
├── CategoryPage (Fashion)
│   ├── ProductPage (Cotton T-Shirt)
│   └── ...
├── ProductIndexPage (Shop)
└── StandardPage (About, Contact, etc.)
```

**Later**: Users → Cart → Checkout → Orders

This order ensures each phase builds on the previous, with clear dependencies and testable milestones. The page-based architecture provides natural URL hierarchy and leverages Wagtail's built-in page management.
