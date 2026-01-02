# E-commerce Development Progress Tracker

> **Quick reference checklist for tracking development progress**
>
> For detailed specifications, see [E-commerce Development Plan](./e-commerce-development-plan.md)

**Last Updated**: Not started

**Current Phase**: Setup

---

## Setup & Prerequisites

- [ ] Docker environment running (`make up`)
- [ ] Database selected (SQLite/PostgreSQL/MySQL)
- [ ] Superuser created (`make superuser`)
- [ ] Frontend assets compiled (`npm run build`)

---

## Phase 1: Foundation Setup

**Goal**: Category system foundation

### Core Tasks
- [ ] Create shop app (`python manage.py startapp shop`)
- [ ] Add shop to INSTALLED_APPS in `app/settings/base.py`
- [ ] Create ProductCategory snippet model
  - Fields: name, slug, description, icon, display_order, is_active
  - Register with `@register_snippet`
- [ ] Run migrations
- [ ] Create sample categories command
  - Command: `python manage.py create_sample_categories`
  - Test with: `--reset`, `--with-icons`
- [ ] Write tests for categories
- [ ] Verify in Wagtail admin: Categories appear in Snippets

**Completion Criteria**:
- [ ] All tasks checked above
- [ ] Categories visible in Wagtail admin
- [ ] Management command runs successfully
- [ ] Tests passing (`make test`)

---

## Phase 2: Product Detail Pages

**Goal**: Individual product pages with images

### Core Tasks
- [ ] Create ProductPage model (extends wagtail.models.Page)
  - Fields: category, price, sku, description, main_image, in_stock, featured, created_at
  - Content panels defined
  - Search fields configured
- [ ] Create ProductImage inline model (gallery)
  - ParentalKey to ProductPage
  - Fields: image, caption, display_order
- [ ] Create product detail template (`app/shop/templates/shop/product_page.html`)
  - Product image, title, category breadcrumb
  - Price display, description
  - Stock status, "Add to Cart" placeholder
  - Image gallery (thumbnail strip)
- [ ] Add styling in extra_css block
- [ ] Run migrations
- [ ] Create sample products command
  - Command: `python manage.py create_sample_products --count=20 --with-images`
  - Test various options
- [ ] Write tests for products and images
- [ ] Verify: Products browsable in Wagtail page tree

**Completion Criteria**:
- [ ] All tasks checked above
- [ ] Product pages render correctly
- [ ] Images display properly
- [ ] Management command creates realistic products
- [ ] Tests passing

---

## Phase 3: Category Browse Pages

**Goal**: Browse products by category

### Core Tasks
- [ ] Create CategoryPage model (extends wagtail.models.Page)
  - Fields: category (FK to ProductCategory), show_featured_only, products_per_page
  - Methods: get_products(), get_context() with pagination
- [ ] Create category page template (`app/shop/templates/shop/category_page.html`)
  - Category header (name, description, icon)
  - Product grid (reuse product card styling)
  - Pagination controls
- [ ] Update navigation
  - Link category cards on home page to CategoryPages
  - Add category menu to header
- [ ] Run migrations
- [ ] Create category pages command
  - Command: `python manage.py create_category_pages`
  - Test with: `--reset`
- [ ] Write tests for category pages and filtering
- [ ] Verify: Category pages show filtered products

**Completion Criteria**:
- [ ] All tasks checked above
- [ ] Category pages display correctly
- [ ] Product filtering works
- [ ] Pagination functional
- [ ] Management command creates all pages
- [ ] Tests passing

---

## Phase 4: Product Listing/Index Page

**Goal**: Main shop page with filtering and search

### Core Tasks
- [ ] Create ProductIndexPage model (extends wagtail.models.Page)
  - Fields: intro, products_per_page, show_filters
  - Methods: get_products(), get_context() with filtering
- [ ] Add filtering functionality
  - GET parameters: category, min_price, max_price, in_stock, featured, sort
  - Pagination support
- [ ] Create product index template (`app/shop/templates/shop/product_index_page.html`)
  - Filter sidebar (category, price range, stock, sort)
  - Product grid
  - Result count, pagination
- [ ] Integrate with search
  - Update `app/search/views.py` to show ProductPages
  - Add search box to header
- [ ] Run migrations
- [ ] Create product index page (via admin or command)
  - Command: `python manage.py setup_product_index` (optional)
  - Slug: `/shop/` or `/products/`
- [ ] Update header navigation to link to shop page
- [ ] Write tests for filtering, sorting, pagination, search
- [ ] Verify: All products browsable with filters working

**Completion Criteria**:
- [ ] All tasks checked above
- [ ] Filtering works correctly
- [ ] Search returns product results
- [ ] Sorting functional
- [ ] Tests passing

---

## Phase 5: Product Enhancements

**Goal**: Variants, specs, reviews, related products

### Core Tasks
- [ ] Create ProductVariant model (inline)
  - Fields: name, variant_type, price_modifier, sku_suffix, in_stock
  - Add to ProductPage as InlinePanel
- [ ] Add product specifications
  - Choose approach: StreamField, TableBlock, or JSONField
  - Update template to display specs
- [ ] Add related products field
  - ParentalManyToManyField to ProductPage
  - Display in template (3-4 related products)
- [ ] Create ProductReview snippet
  - Fields: author_name, rating, comment, created_at, is_approved
  - Add review submission form
  - Display approved reviews on product page
- [ ] Add breadcrumbs
  - Template tag or include
  - Show: Home > Category > Product
- [ ] Optimize images
  - Create renditions: 200x200, 400x400, 800x800
  - Update templates to use renditions
- [ ] Create enhancement command
  - Command: `python manage.py enhance_sample_products`
  - Options: `--variants-only`, `--reviews-only`, `--related-only`, `--reset`
- [ ] Run migrations
- [ ] Write tests for variants, specs, reviews, related products
- [ ] Verify: All enhancements working

**Completion Criteria**:
- [ ] All tasks checked above
- [ ] Variants selectable
- [ ] Reviews display and submission works
- [ ] Related products show
- [ ] Breadcrumbs appear
- [ ] Management command enhances products
- [ ] Tests passing

---

## Phase 6: Supporting Content Pages

**Goal**: Info pages and contact form

### Core Tasks
- [ ] Create StandardPage model (StreamField for body)
- [ ] Create ContactFormPage model (wagtail.contrib.forms)
  - Fields: name, email, subject, message
  - Email notification setup
- [ ] Create templates for content pages
- [ ] Create specific pages:
  - [ ] About Us
  - [ ] FAQ
  - [ ] Shipping & Returns
  - [ ] Terms & Conditions
  - [ ] Privacy Policy
  - [ ] Contact page with form
- [ ] Update footer links to actual pages
- [ ] Create content pages command
  - Command: `python manage.py create_content_pages`
  - Options: `--reset`, `--pages=about,faq`
- [ ] Write tests for content pages and contact form
- [ ] Verify: All info pages accessible, contact form works

**Completion Criteria**:
- [ ] All tasks checked above
- [ ] All info pages created
- [ ] Contact form submits successfully
- [ ] Footer links functional
- [ ] Management command creates pages
- [ ] Tests passing

---

## Quick Commands Reference

### Database Reset
```bash
make down && make up && make migrate
make superuser
```

### Run All Phase Commands
```bash
# Phase 1
python manage.py create_sample_categories

# Phase 2
python manage.py create_sample_products --count=50 --with-images

# Phase 3
python manage.py create_category_pages

# Phase 4
python manage.py setup_product_index

# Phase 5
python manage.py enhance_sample_products

# Phase 6
python manage.py create_content_pages
```

### Testing
```bash
make test                    # Run all tests
make sh                      # Enter container shell
python manage.py test app.shop.tests  # Test shop app only
```

### Frontend
```bash
npm run build                # Build production assets
npm start                    # Watch mode for development
```

---

## Notes & Decisions

_Use this section to track important decisions, blockers, or notes as you work_

- **[Date]**: Decision/Note here
- **[Date]**: Issue encountered and resolution

---

## Next Steps

When resuming work:
1. Check which phase is current (see "Current Phase" at top)
2. Review unchecked tasks in that phase
3. Run `make test` to verify current state
4. Continue with next unchecked task

For detailed implementation specs, always refer to [E-commerce Development Plan](./e-commerce-development-plan.md)
