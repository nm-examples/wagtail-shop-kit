# Management Commands Documentation

This document provides detailed information about the custom Django management commands available in this Wagtail project.

## Table of Contents

- [create_sample_media](#create_sample_media)
- [create_sample_categories](#create_sample_categories)
- [Future Commands](#future-commands)

---

## create_sample_media

**Location**: `app/home/management/commands/create_sample_media.py`

**Purpose**: Creates sample images and documents (media files) for testing and demonstration purposes in your Wagtail CMS.

### Description

The `create_sample_media` command generates realistic sample content including:

- **Dynamic Images**: Programmatically generated JPEG images with random colors, shapes, and text overlays
- **Text Documents**: Structured text files with realistic business content
- **ZIP Archives**: Compressed archives containing collections of documents with README files

This command is perfect for:
- Populating a new Wagtail site with test content
- Demonstrating media management features
- Testing search functionality with varied content
- Creating realistic data for development and staging environments

### Usage

```bash
# Basic usage (creates 75 images and 50 documents by default)
python manage.py create_sample_media

# Custom amounts
python manage.py create_sample_media --images 20 --documents 10

# Clear existing content and create new
python manage.py create_sample_media --clear --images 15 --documents 8

# Create content without ZIP archives
python manage.py create_sample_media --no-zip

# Only delete existing content (no new content created)
python manage.py create_sample_media --reset
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--images` | Integer | 75 | Number of sample images to create |
| `--documents` | Integer | 50 | Number of sample documents to create |
| `--clear` | Flag | False | Clear existing images and documents before creating new ones |
| `--no-zip` | Flag | False | Skip creating ZIP archives of the documents |
| `--reset` | Flag | False | Delete all existing images and documents without creating new ones |

### Generated Content Details

#### Images
- **Formats**: JPEG with 85% quality
- **Sizes**: Multiple dimensions including landscape (800x600), portrait (600x800), banners (1200x400), squares (400x400), and standard (1024x768)
- **Visual Elements**: Random geometric shapes, lines, and color combinations
- **Text Overlay**: Truncated version of the image title
- **Titles**: Unique combinations using descriptive words, subjects, and random numbers
  - Example: `"Vibrant Abstract Art #749"`
  - Example: `"Modern Architecture - Technology #321"`

#### Documents
- **Format**: UTF-8 encoded text files (.txt)
- **Structure**: Professional document layout with headers, metadata, and sections
- **Content**: Realistic business document types including:
  - Project Reports
  - User Manuals
  - Technical Specifications
  - Meeting Notes
  - Policy Documents
  - Training Materials
  - Research Findings
  - Implementation Guides
  - Quality Assurance Checklists
  - Release Notes
- **Titles**: Unique combinations using modifiers, contexts, projects, and random numbers
  - Example: `"Strategic Project Report for Development Team #7549"`
  - Example: `"User Manual - Phoenix Initiative #3281"`

#### ZIP Archives
When not using `--no-zip`, the command creates:

1. **Complete Archive**: Contains all generated documents plus a README
2. **Themed Archives**: Smaller collections grouped by type:
   - Project Documentation Bundle
   - Technical Resources Collection
   - User Guides and Manuals

Each ZIP file includes:
- All relevant documents
- A README.txt file explaining the archive contents
- Proper file organization

### Examples

#### Creating a small test set
```bash
docker exec -it wagtail-shop-kit-app-1 python manage.py create_sample_media --images 5 --documents 3 --no-zip
```

#### Setting up a demo environment
```bash
docker exec -it wagtail-shop-kit-app-1 python manage.py create_sample_media --clear --images 25 --documents 15
```

#### Cleaning up all test content
```bash
docker exec -it wagtail-shop-kit-app-1 python manage.py create_sample_media --reset
```

### Technical Implementation

#### Dependencies
- **PIL (Pillow)**: For dynamic image generation
- **zipfile**: For creating compressed archives
- **Wagtail**: Uses `wagtail.images.models.Image` and `wagtail.documents.models.Document`

---

## create_sample_categories

**Location**: `app/shop/management/commands/create_sample_categories.py`

**Purpose**: Creates a shop index page and sample category pages for the e-commerce section of your Wagtail site.

### Description

The `create_sample_categories` command sets up the foundational structure for your online shop by:

1. **Creating or finding a ShopIndexPage**: Automatically creates a main "Shop" page under the home page if it doesn't already exist
2. **Creating Category Pages**: Generates 6 sample category pages (Electronics, Fashion, Home & Living, Beauty, Sports, Books) as children of the shop index page
3. **Assigning Icons**: Optionally assigns random images from your media library as category icons
4. **Publishing Content**: All pages are automatically published and ready to view

This command is perfect for:
- Setting up a new e-commerce site structure
- Demonstrating shop browsing functionality
- Creating realistic category data for development
- Testing the shop page hierarchy

### Usage

```bash
# Basic usage (creates shop index and 6 categories with icons)
python manage.py create_sample_categories

# Reset and recreate all categories
python manage.py create_sample_categories --reset

# Create categories without icons
python manage.py create_sample_categories --no-icons

# Custom shop page configuration
python manage.py create_sample_categories --shop-title "Store" --shop-slug "store"

# Use a different home page
python manage.py create_sample_categories --home-slug "homepage"
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--reset` | Flag | False | Delete all existing category pages before creating new ones |
| `--no-icons` | Flag | False | Skip assigning icons to categories |
| `--home-slug` | String | "home" | Slug of the home page where shop index will be created |
| `--shop-title` | String | "Shop" | Title for the shop index page |
| `--shop-slug` | String | "shop" | Slug for the shop index page |

### Generated Content Details

#### ShopIndexPage
- **Location**: Created as a child of the home page
- **Default URL**: `/shop/`
- **Properties**:
  - Title: "Shop" (customizable)
  - Intro text: "Browse our collection of quality products across various categories."
  - Visible in menus: Yes
  - Max count: 1 (only one shop index page allowed)

#### Category Pages
The command creates 6 category pages with the following structure:

| Category | Slug | Featured | Description Theme |
|----------|------|----------|-------------------|
| Electronics | electronics | Yes | Gadgets, tech products, smartphones, laptops |
| Fashion | fashion | Yes | Clothing, accessories, styles, trends |
| Home & Living | home-living | Yes | Furniture, decor, interior design |
| Beauty | beauty | No | Skincare, cosmetics, beauty products |
| Sports | sports | No | Fitness equipment, outdoor gear |
| Books | books | No | Novels, educational resources, guides |

Each category includes:
- **Rich text description**: HTML formatted text with multiple paragraphs
- **Icon**: Random image from your media library (if available and not using `--no-icons`)
- **Featured flag**: First 3 categories are marked as featured
- **Menu visibility**: All categories are visible in navigation menus

### Page Hierarchy

The command creates the following page structure:

```
Home
└── Shop (ShopIndexPage)
    ├── Beauty (ShopCategoryPage)
    ├── Books (ShopCategoryPage)
    ├── Electronics (ShopCategoryPage) ⭐ Featured
    ├── Fashion (ShopCategoryPage) ⭐ Featured
    ├── Home & Living (ShopCategoryPage) ⭐ Featured
    └── Sports (ShopCategoryPage)
```

### Examples

#### Creating categories in Docker
```bash
docker exec -it wagtail-shop-kit-app-1 python manage.py create_sample_categories
```

#### Creating categories with make command
```bash
make sh
python manage.py create_sample_categories
```

#### Resetting and recreating with different configuration
```bash
docker exec -it wagtail-shop-kit-app-1 python manage.py create_sample_categories \
  --reset \
  --shop-title "Store" \
  --shop-slug "store"
```

#### Creating without icons (faster, no media dependencies)
```bash
docker exec -it wagtail-shop-kit-app-1 python manage.py create_sample_categories --no-icons
```

### Prerequisites

- A home page must exist in your Wagtail site (default slug: "home")
- For icons: Run `python manage.py create_sample_media` first to generate sample images

### Output Example

```
Found existing ShopIndexPage: 'Shop' at /shop/
Found 75 images available for category icons
  Assigning icon: Sharp City Skyline #469 (ID: 29)
  ✓ Created: Electronics 🖼️  (icon: Sharp City Skyline #469...) ⭐ [FEATURED]
  Assigning icon: Handcrafted Garden Abstract Art #415 (ID: 44)
  ✓ Created: Fashion 🖼️  (icon: Handcrafted Garden Abstract Ar...) ⭐ [FEATURED]
  ...

============================================================
Successfully created 6 category pages under 'Shop'

Category URLs:
  → /shop/beauty/ - Beauty
  → /shop/books/ - Books
  → /shop/electronics/ - Electronics
  → /shop/fashion/ - Fashion
  → /shop/home-living/ - Home & Living
  → /shop/sports/ - Sports
============================================================
```

### Technical Implementation

#### Dependencies
- **Wagtail Page Models**: Uses `ShopIndexPage` and `ShopCategoryPage` from `app.shop.models`
- **Wagtail Images**: Optionally uses `wagtail.images.models.Image` for category icons
- **Treebeard**: Leverages Wagtail's page tree structure for parent-child relationships

#### Key Features
- **Idempotent**: Safe to run multiple times; checks for existing pages before creating
- **Tree Cache Management**: Properly refreshes page tree after deletions to prevent cache issues
- **Random Icon Assignment**: Shuffles available images to assign unique icons to each category
- **Revision Management**: Creates and publishes page revisions automatically

---

## Future Commands

This section will be expanded as additional management commands are added to the project.
