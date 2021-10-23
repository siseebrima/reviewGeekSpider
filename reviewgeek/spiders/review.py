import scrapy
import json


def parse_review(response):
    title = response.xpath('//meta[@property="og:title"]/@content').get()
    pic = response.xpath('//meta[@property="og:image"]/@content').get()
    summary = response.xpath('//meta[@property="og:description"]/@content').get()
    sid = response.xpath('//input[@name="postid"]/@value').getall()[1]
    verdict = response.xpath('//div[@class="single-review-card border"]/preceding-sibling::p[position() < 4]//text()').get()

    data = json.loads(response.xpath('//script[@type="application/ld+json"][2]//text()').extract_first())

    if data:
        try:
            rating = data['review']['reviewRating']['ratingValue']
            author = data['review']['author']['name']
            date = data['review']['datePublished']
        except Exception as e:
            print(e)

    if "Review:" in title:
        product_name = title.split('Review:')[0]
    else:
        product_name = title

    yield {
        'Title': title,
        'Pic': pic,
        'Summary': summary,
        'SID': sid,
        'Product Name': product_name,
        'Rating': rating,
        'Scale': 10,
        'Author': author,
        'Date': date,
        'URL': response.url,
        'Verdict': verdict
    }


class ReviewSpider(scrapy.Spider):
    name = 'review'
    allowed_domains = ['www.reviewgeek.com']
    start_urls = ['https://www.reviewgeek.com/t/single-review/']

    page = 2

    def parse(self, response):
        links = response.xpath('//header/a/@href').getall()

        for link in links:
            yield response.follow(link, callback=parse_review)

        next_page_url = 'https://www.reviewgeek.com/t/single-review/page/' + str(self.page) + '/'

        if self.page < 43:
            yield response.follow(next_page_url, callback=self.parse)
            self.page += 1


