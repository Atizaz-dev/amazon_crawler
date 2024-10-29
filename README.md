---

# Amazon Brand Product Data Scraper with Django, Celery & Scrapy

A scalable web scraping solution built with Django, Celery, and Scrapy to automate Amazon brand product data collection and keep information up-to-date with periodic updates.

## Contents
1. [Project Summary](#project-summary)
2. [Key Highlights](#key-highlights)
3. [Installation and Setup](#installation-and-setup)
    - [System Requirements](#system-requirements)
    - [Install Instructions](#install-instructions)
4. [How to Start the Application](#how-to-start-the-application)
    - [Configure Django](#configure-django)
    - [Configure Celery](#configure-celery)
5. [Scraper Functionality](#scraper-functionality)
6. [Technical Design and Assumptions](#technical-design-and-assumptions)

## Project Summary

This project is designed for efficient, automated collection of product data from Amazon for specific brands. It integrates a Django backend to manage brand information and control scraping tasks, Celery for scheduling and background processing, and Scrapy to perform the web scraping. Key product details retrieved include:
- **Product Name**
- **ASIN** (Amazon Standard Identification Number)
- **SKU**
- **Image URL**

The project is configured to scrape data automatically multiple times a day and includes mechanisms to prevent scraping interruptions.

## Key Highlights

- **Django-Based Backend**: Provides a simple interface to manage brand data and administer scraping settings.
- **Automated Scraping with Celery**: Scheduled tasks using Celery ensure product data is updated throughout the day without manual intervention.
- **Resilient and Scalable**: Error handling, retries, and scheduling ensure robustness for production environments.
- **Redis Integration**: Redis serves as the message broker to coordinate Celery tasks and manage background operations effectively.

---

## Installation and Setup

### System Requirements
- **Python 3.10** or higher
- **Django** for the backend
- **Celery** for task scheduling and background jobs
- **Redis** to act as the message broker for Celery
- **Scrapy** for the scraping functionality

### Install Instructions

1. Clone the repository and navigate to the project directory.
2. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Install **Redis**:
   - For Windows, download the Redis executable from [Redis for Windows](https://github.com/tporadowski/redis/releases) and follow the installation steps.
   - For Mac and Linux, use the package manager:
     ```bash
     # Mac
     brew install redis
     # Linux
     sudo apt-get install redis-server
     ```

4. Start the Redis server and verify installation by running `redis-cli` and typing `PING`. A successful setup will return `PONG`.

---

## How to Start the Application

### Configure Django

1. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create an Admin User** for Django’s backend:
   ```bash
   python manage.py createsuperuser
   ```

3. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000`.

### Configure Celery

1. Add Celery configuration settings in `settings.py`, setting Redis as the broker:

    ```python
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_BEAT_SCHEDULE = {
       'scrape-marketminer-products-every-6-hours': {
        'task': 'merchandise.tasks.scrape_brands',
        'schedule': crontab(hour='*/6'),  # can change the time for testing purpose
    },
    }
    CELERY_TIMEZONE = 'UTC'
    ```

2. **Launch Celery Worker**:
   Open a terminal and start the Celery worker:

    ```bash
    python -m celery -A MarketMiner worker --pool=solo --loglevel=info


    ```

3. **Start Celery Beat**:
   In a new terminal, initialize the Celery Beat scheduler to manage periodic tasks:

    ```bash
    python -m celery -A MarketMiner beat --loglevel=info

    ```

## Functionality

The Scrapy spider is tailored for brand-specific data extraction on Amazon. It automatically cycles through the product pages to gather all available information, handling pagination smoothly and rotating headers to avoid detection. Key features include:

- **Multi-Page Scraping**: Traverses multiple pages of Amazon’s brand search results.
- **Data Parsing**: Extracts essential details like product name, ASIN, SKU, and image URL.
- **Automatic Data Updates**: Product data is kept current by updating existing entries (using ASIN as a unique identifier) or adding new products.
- **Bulk Data Creation**: Supports bulk creation of product entries in batches of 20, ensuring efficient database updates. This batch size can be modified to suit different scraping needs, allowing for flexibility in managing data volume.

Here’s an example of a **FrontEnd** section for the README file, describing the Bootstrap-based brand and product listing page with search functionality.

---

## FrontEnd

The frontend for this application displays a list of brands and their associated products using a clean and responsive Bootstrap layout. This page includes a search bar to filter products, making it easy for users to find specific items across all brands. The core elements of the frontend are:

### Features

- **Responsive Layout**: Built with Bootstrap for responsiveness, the layout automatically adjusts for various screen sizes, ensuring a user-friendly experience on both desktop and mobile devices.
- **Brand Display**: Each brand and its products are shown in separate, visually distinct Bootstrap cards for better organization.
- **Product List**: Products are displayed within each brand card as a list, including the product name, ASIN, and a thumbnail image.
- **Search Functionality**: A search bar allows users to search for specific products across all brands. The search term persists after submission, displaying the filtered product list based on the query.

### Frontend Structure

The main HTML template for the frontend is styled with Bootstrap and consists of:
- **Search Bar**: The search bar is built with a Bootstrap inline form, allowing users to enter a product name or term to filter results.
- **Brand Cards**: Each brand is contained within a Bootstrap card, which displays the brand name and a list of its products.
- **Product List Items**: Each product is displayed as a list item within the brand card, showing key information and a small product image.

This setup makes it easy to extend or modify the layout if needed, allowing for a scalable frontend design. 
Based on the details provided, here’s an added section for the README focused solely on implemented features:

---

### Anti-Scraping Measures

The following anti-scraping techniques are implemented to reduce the likelihood of request blocking:

- **User-Agent Rotation**: To simulate requests from different browsers, user-agent strings are rotated during scraping.
- **Error Handling and Retries**: Scrapy's built-in retry mechanism is used to handle failed requests, ensuring data completeness.

### Design Decisions and Assumptions

- **Django-Celery-Scrapy Architecture**: Django manages data and backend functions, Celery schedules and executes periodic tasks, and Scrapy handles data scraping. This modular setup allows for easy extension and maintenance.
- **Data Integrity with ASIN**: Each product’s ASIN is used as a unique identifier, allowing for efficient updates without duplicating entries.

--- 

### Task Scheduling
Celery Beat handles the scheduling for regular scraping, set to execute every 6 hours. This timing can be modified in `settings.py` by adjusting the crontab configuration.


