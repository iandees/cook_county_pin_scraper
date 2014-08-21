# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CSVFeedSpider

from cook_county_pin_scraper.items import Property

class PropertyinfoSpider(CSVFeedSpider):
    headers = ['pin']
    name = "propertyinfo"
    allowed_domains = ["www.cookcountypropertyinfo.com"]
    start_urls = (
        'file:///Users/iandees/Downloads/PINs for Ian/pins-unique.txt',
        # 'http://www.cookcountypropertyinfo.com/Pages/PIN-Results.aspx?PIN=17092620240000',
    )

    def parse_row(self, response, row):
        pin = row['pin']
        return scrapy.Request('http://www.cookcountypropertyinfo.com/Pages/PIN-Results.aspx?PIN='+pin, callback=self.parse_pin)

    def extract_with_prefix(self, response, suffix, inner_part=''):
        ext = response.xpath('//span[@id="ctl00_PlaceHolderMain_ctl00_{}"]{}/text()'.format(suffix, inner_part))
        if len(ext) == 1:
            return ext[0].extract()
        else:
            return None

    def parse_pin(self, response):
        item = Property()

        item['property_tax_year'] = self.extract_with_prefix(response, 'propertyTaxYear', '/b')
        if item['property_tax_year']:
            item['property_tax_year'] = int(item['property_tax_year'][-4:])

        item['pin'] = self.extract_with_prefix(response, 'propertyPIN')
        item['address'] = self.extract_with_prefix(response, 'propertyAddress')
        item['city'] = self.extract_with_prefix(response, 'propertyCity')
        item['zip_code'] = self.extract_with_prefix(response, 'propertyZip')
        item['township'] = self.extract_with_prefix(response, 'propertyTownship')

        item['assessment_tax_year'] = self.extract_with_prefix(response, 'assessmentTaxYear', '/b')
        if item['assessment_tax_year']:
            item['assessment_tax_year'] = int(item['assessment_tax_year'][-4:])

        item['estimated_value'] = self.extract_with_prefix(response, 'propertyEstimatedValue')
        if item['estimated_value']:
            item['estimated_value'] = int(item['estimated_value'].replace('$','').replace(',',''))

        item['assessed_value'] = self.extract_with_prefix(response, 'propertyAssessedValue')
        if item['assessed_value']:
            item['assessed_value'] = int(item['assessed_value'].replace('$','').replace(',',''))

        item['lot_size'] = self.extract_with_prefix(response, 'propertyLotSize')
        if item['lot_size']:
            item['lot_size'] = int(item['lot_size'].replace(',', ''))

        item['building_size'] = self.extract_with_prefix(response, 'propertyBuildingSize')
        if item['building_size']:
            item['building_size'] = int(item['building_size'].replace(',', ''))

        item['property_class'] = self.extract_with_prefix(response, 'propertyClass')
        item['property_class_description'] = self.extract_with_prefix(response, 'msgPropertyClassDescription')
        item['building_age'] = self.extract_with_prefix(response, 'propertyBuildingAge')

        item['mailing_tax_year'] = self.extract_with_prefix(response, 'mailingTaxYear', '/b')
        if item['mailing_tax_year']:
            item['mailing_tax_year'] = int(item['mailing_tax_year'][-4:])
        item['mailing_name'] = self.extract_with_prefix(response, 'propertyMailingName')
        item['mailing_address'] = self.extract_with_prefix(response, 'propertyMailingAddress')
        item['mailing_city_state_zip'] = self.extract_with_prefix(response, 'propertyMailingCityStateZip')

        item['tax_rate_year'] = int(self.extract_with_prefix(response, 'taxRateTaxYear')[1:5])
        item['tax_rate'] = float(self.extract_with_prefix(response, 'propertyTaxRate'))
        item['tax_code_year'] = int(self.extract_with_prefix(response, 'taxCodeTaxYear')[1:5])
        item['tax_code'] = self.extract_with_prefix(response, 'propertyTaxCode')

        yield item
