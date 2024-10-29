import logging
import scrapy
from merchandise.models import Brand, Product
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from utilities import get_proxy

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "device-memory": "8",
    "downlink": "1.4",
    "dpr": "1.25",
    "ect": "3g",
    "priority": "u=0, i",
    "rtt": "300",
    "sec-ch-device-memory": "8",
    "sec-ch-dpr": "1.25",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua-platform-version": "\"10.0.0\"",
    "sec-ch-viewport-width": "1042",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "viewport-width": "1042"
}
logger = logging.getLogger('scraping')


class MarketMinerSpider(scrapy.Spider):
    name = "products_data"

    def __init__(self, brand, batch_size=20, *args, **kwargs):
        super(MarketMinerSpider, self).__init__(*args, **kwargs)
        self.brand = brand
        self.batch_size = batch_size
        self.product_batch = []

    def start_requests(self):
        url = f'https://www.amazon.com/s?k={self.brand}&crid=2K5HA2CNE4A8S&sprefix=step+2%2Caps%2C165&ref=nb_sb_noss_1'
        meta = {'proxy': get_proxy(), 'brand': self.brand}
        yield scrapy.Request(
            url,
            headers=HEADERS, meta=meta)

    def parse(self, response, **kwargs):
        for url in response.css("h2 > a.a-link-normal::attr(href)").getall():
            url = url.split('?')[0]
            meta = {'proxy': get_proxy(), 'brand': response.meta.get('brand')}

            yield response.follow(url, callback=self.parse_details, headers=HEADERS, meta=meta)

        next_page_url = response.css("a.s-pagination-next::attr(href)").get()
        if next_page_url:
            next_page_url = next_page_url.split('&xpid')[0]
            meta = {'proxy': get_proxy(), 'brand': response.meta.get('brand')}

            yield response.follow(next_page_url, callback=self.parse, meta=meta, headers=HEADERS)

    def parse_details(self, response, **kwargs):
        try:
            product_name = response.css('span#productTitle::text').get('').strip()
            asin = response.css("th:contains('ASIN') + td::text").get('').strip()
            image_url = response.css('div#imgTagWrapperId>img::attr(src)').get('').strip()
            brand_name = response.meta.get('brand')
            self.product_batch.append({
                'brand_name': brand_name,
                'product_name': product_name,
                'asin': asin,
                'image_url': image_url,
                'product_url': response.url,
            })
            if len(self.product_batch) >= self.batch_size:
                self.save_data()
            logger.info(f"Queued product {product_name} (ASIN: {asin}) for brand {brand_name}")
        except Exception as e:
            logger.error(f"Error scraping product for brand {response.meta.get('brand')}: {e}")

    def save_data(self):
        try:
            for item in self.product_batch:
                brand, _ = Brand.objects.get_or_create(name=item['brand_name'])
                product, created = Product.objects.update_or_create(
                    asin=item['asin'],
                    defaults={
                        'name': item['product_name'],
                        'image': item['image_url'],
                        'brand': brand,
                        'sku': None
                    }
                )
                action = "Created" if created else "Updated"
                logger.info(f"{action} product {product.name} (ASIN: {product.asin}) for brand {brand.name}")
            self.product_batch = []
        except Exception as e:
            logger.error(f"Error during save operation: {e}")

    def close(self, reason):
        if self.product_batch:
            self.save_data()
        super().close(reason)


def scrape_merchandise(brand_name):
    file_name = f"{brand_name}_data.json"

    local_setting = get_project_settings()
    local_setting.set('BOT_NAME', 'amazon')
    local_setting['FEED_FORMAT'] = 'json'
    local_setting['FEED_URI'] = file_name
    local_setting['CONCURRENT_REQUESTS'] = 5
    local_setting['ROBOTSTXT_OBEY'] = False
    local_setting['DOWNLOAD_DELAY'] = 2
    local_setting['RETRY_TIMES'] = 10

    local_setting['RETRY_HTTP_CODES'] = [500, 502, 503, 504, 400, 403, 404, 408]
    local_setting[
        'USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
    local_setting['LOG_LEVEL'] = 'DEBUG'
    local_setting['HTTPCACHE_ENABLED'] = True
    local_setting['HTTPCACHE_EXPIRATION_SECS'] = 3600
    local_setting['HTTPCACHE_DIR'] = 'httpcache'
    local_setting['HTTPCACHE_IGNORE_HTTP_CODES'] = [500, 502, 503, 504, 400, 403, 404, 408]

    process = CrawlerProcess(local_setting)
    crawler = process.create_crawler(MarketMinerSpider)

    process.crawl(crawler, brand=brand_name)
    process.start()
