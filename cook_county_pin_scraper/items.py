# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Property(scrapy.Item):
    pin = scrapy.Field()
    property_tax_year = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    zip_code = scrapy.Field()
    township = scrapy.Field()

    assessment_tax_year = scrapy.Field()
    estimated_value = scrapy.Field()
    assessed_value = scrapy.Field()
    lot_size = scrapy.Field()
    building_size = scrapy.Field()
    property_class = scrapy.Field()
    property_class_description = scrapy.Field()
    building_age = scrapy.Field()

    mailing_tax_year = scrapy.Field()
    mailing_name = scrapy.Field()
    mailing_address = scrapy.Field()
    mailing_city_state_zip = scrapy.Field()

    tax_rate_year = scrapy.Field()
    tax_rate = scrapy.Field()
    tax_code_year = scrapy.Field()
    tax_code = scrapy.Field()

    tax_bills = scrapy.Field()
