import scrapy
from string import ascii_uppercase

CCEL = 'http://www.ccel.org'


class BlogSpider(scrapy.Spider):
    name = 'ccelspider'
    start_urls = ['{}'.format(CCEL)]

    def __init__(self):
        self.titles = set()

    def parse(self, response):
        for letter in ascii_uppercase:
            url = '/index/title/{}'.format(letter)
            yield scrapy.Request(response.urljoin(url), self.parse_titles)

    def parse_titles(self, response):
        book_title = None
        for book_page in response.css('#content > .hang'):
            book_title = book_page.css('a::text').extract()[0]
            book_text = book_page.css('a::attr("href")').extract()[0][:-5]
            book_text_url = '{}.txt'.format(book_text)
            self.titles.add(book_text_url)
            request = scrapy.Request(response.urljoin(book_text_url), self.download_book)
            request.meta['title'] = book_title
            yield request

    def download_book(self, response):
        title = 'books/{}.txt'.format(response.meta['title'])
        try:
            with open(title, 'w') as f:
                f.write(response.text)
        except Exception as e:
            print(e)
        yield None
