import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import SpaenglerItem
from itemloaders.processors import TakeFirst
pattern = r'(\r)?(\n)?(\t)?(\xa0)?(-{1,})?'

class SpaenglerSpider(scrapy.Spider):
	name = 'spaengler'
	start_urls = ['https://www.pressefach.info/spaengler',
				  'https://www.pressefach.info/spaengler/pressemeldungen.htm'
				  ]

	def parse(self, response):
		post_links = response.xpath('//table//font[@style="vertical-align: inherit;"]/a[@style="font-weight: 700; text-decoration:none"]/@href | //a[@style="font-weight: 700; text-decoration:none"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)


	def parse_post(self, response):

		date = ''.join(response.xpath('//td//text()').getall())
		date = re.findall(r'\d+\.\d+\.\d+',date)
		title = ''.join(response.xpath('//p[@class="MsoNormal"]//font[@size="3"]//text() | //span[@style="font-size: 12.0pt; font-family: Verdana,sans-serif; color: black; font-weight: bold"]//text() | //p[@class="MsoNormal"]/b[1]/span/text()').getall()).strip()
		title = re.sub(pattern, "", title)
		if not title:
			title = "PRESSEAUSSENDUNG Bankhaus Spängler"
		content = response.xpath('//td[@bgcolor="#F7F7F7"]//text()').getall()
		content = [p.strip() for p in content if p.strip() and 'pdf'.upper().lower() not in content]
		content = re.sub(pattern, "",' '.join(content)).replace('\n   ','')


		item = ItemLoader(item=SpaenglerItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
