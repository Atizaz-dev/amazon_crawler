import logging

from celery import shared_task

from utilities.data_extractor import scrape_merchandise
from .models import Brand

logger = logging.getLogger('scraping')


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60})
def scrape_brands(self):
    """
    Executes the scraping function for each brand in the Brand model.
    Logs progress and exceptions.
    """
    logger.info("Initiating scraping task across all registered brands.")

    # Query and log the count of brands to be processed
    brand_queryset = Brand.objects.all()
    brand_count = brand_queryset.count()
    logger.info(f"{brand_count} brands found in the database.")

    for index, brand in enumerate(brand_queryset, start=1):
        try:
            logger.info(f"[{index}/{brand_count}] Scraping started for brand: {brand.name}")
            scrape_merchandise(brand.name)
            logger.info(f"[{index}/{brand_count}] Successfully completed scraping for: {brand.name}")
        except Exception as e:
            logger.exception(f"Scraping failed for brand '{brand.name}' with error: {str(e)}")

    logger.info("All brand scraping tasks have been processed.")
