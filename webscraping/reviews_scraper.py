import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, parse_qs


class ReviewSpider(scrapy.Spider):
    name = 'reviewspider'
    start_url = 'https://reviews.webmd.com/vitamins-supplements/ingredientreview-998-MAGNESIUM?conditionid=&sortval=1&page=1&next_page=true'
    # изменить ссылку для другого БАДа

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse)

    custom_settings = {
        'FEEDS': {'reviews_Magnesium.csv': {'format': 'csv'}}
         # изменить название файла
    }

    def parse(self, response):
        for review_details in response.css('div.review-details-holder'):
            reviews = review_details.css('p.description-text::text').getall()

            if not reviews:
                reviews_1 = review_details.css('span.showSec::text').getall()
                reviews_2 = review_details.css('span.hiddenSec::text').getall()
                reviews = reviews_1 + reviews_2

            yield {
                "dates": review_details.css('div.date::text').getall(),
                "details": review_details.css('div.details::text').getall(),
                "scores": review_details.css('strong::text').getall(),
                "reviews": reviews,

            }

        parsed_url = urlparse(response.url)
        current_page = int(parse_qs(parsed_url.query)['page'][0])
        next_page = current_page + 1
        if next_page <= 14:    # изменить количество страниц (10=10)
            next_url = f'https://reviews.webmd.com/vitamins-supplements/ingredientreview-998-MAGNESIUM?conditionid=&sortval=1&page={next_page}&next_page=true'
            # изменить ссылку
            yield response.follow(next_url, callback=self.parse)


process = CrawlerProcess()
process.crawl(ReviewSpider)
process.start()