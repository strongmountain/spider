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
            title = 'tocs/{}.txt'.format(book_title)
            url = book_page.css('a::attr("href")').extract()[0][:-5]
            book_text_url = '{}.toc'.format(url)
            self.titles.add(book_text_url)
            request = scrapy.Request(response.urljoin(book_text_url), self.open_book)
            request.meta['title'] = title
            yield request

    def open_book(self, response):
        title = response.meta['title']
        toc = self.get_toc(response.css('#di'))
        text = []
        for content in toc:
            text.append(content)
        try:
            with open(title, 'a') as f:
                f.write(str(text))
        except Exception as e:
            print(e)
        yield None

    def get_toc(self, nodes):
        previous = None
        for node in nodes.xpath('node()'):
            text = self.get_toc_text(node)
            # two p in a row
            if text and previous:
                to_yield = previous
                previous = text
                yield to_yield
            # div part of p + div
            if not text and previous:
                to_yield = previous
                to_yield['children'] = []
                toc = self.get_toc(node)
                for content in toc:
                    to_yield['children'].append(content)
                previous = None
                yield to_yield
            # first p or p + div
            if text and not previous:
                previous = text

    def get_toc_text(self, node):
        text = node.xpath('./a[2]/text()').extract() or node.xpath('./a').css('.TOC::text').extract()
        if not text:
            return None
        url = node.css('.TOC::attr("href")').extract()
        return {'text': text, 'url': url}
