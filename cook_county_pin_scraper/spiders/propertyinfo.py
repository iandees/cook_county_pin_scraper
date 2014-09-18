# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CSVFeedSpider
from collections import OrderedDict
from cook_county_pin_scraper.items import Property

class PropertyinfoSpider(CSVFeedSpider):
    headers = ['pin']
    name = "propertyinfo"
    allowed_domains = ["www.cookcountypropertyinfo.com"]
    start_urls = (
        'file:///mnt/tmp/cook_county_pin_scraper/unique_pins.txt',
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
        if self.extract_with_prefix(response, 'resultsNotFoundPanel'):
            yield None

        item = Property()

        item['property_tax_year'] = self.extract_with_prefix(response, 'propertyTaxYear', '/b')
        if item['property_tax_year']:
            item['property_tax_year'] = int(item['property_tax_year'][-4:])

        item['pin'] = self.extract_with_prefix(response, 'propertyPIN')
        item['address'] = self.extract_with_prefix(response, 'propertyAddress')
        item['city'] = self.extract_with_prefix(response, 'propertyCity')
        item['zip_code'] = self.extract_with_prefix(response, 'propertyZip')
        item['township'] = self.extract_with_prefix(response, 'propertyTownship')

        item['lot_size'] = self.extract_with_prefix(response, 'propertyLotSize')
        if item['lot_size']:
            item['lot_size'] = int(item['lot_size'].replace(',', ''))

        item['building_size'] = self.extract_with_prefix(response, 'propertyBuildingSize')
        if item['building_size']:
            item['building_size'] = int(item['building_size'].replace(',', ''))

        item['property_class'] = {
            'class': self.extract_with_prefix(response, 'propertyClass'),
            'description': self.extract_with_prefix(response, 'msgPropertyClassDescription').split(' - ')[1]
        }
        item['building_age'] = self.extract_with_prefix(response, 'propertyBuildingAge')

        mailing_tax_year = self.extract_with_prefix(response, 'mailingTaxYear', '/b')
        if mailing_tax_year:
            mailing_tax_year = int(mailing_tax_year[-4:])
        mailing_name = self.extract_with_prefix(response, 'propertyMailingName')
        mailing_address = self.extract_with_prefix(response, 'propertyMailingAddress')
        mailing_city_state_zip = self.extract_with_prefix(response, 'propertyMailingCityStateZip')
        item['mailing_address'] = OrderedDict([
            ('year', mailing_tax_year),
            ('name', mailing_name),
            ('address', mailing_address),
            ('city_state_zip', mailing_city_state_zip),
        ])

        years = OrderedDict()
        for i in range(1, 6):
            bill_year = self.extract_with_prefix(response, 'rptTaxBill_ctl0{}_taxBillYear'.format(i))
            if bill_year:
                bill_year = int(bill_year)
            bill_amount = self.extract_with_prefix(response, 'rptTaxBill_ctl0{}_taxBillAmount'.format(i), '/font')
            if bill_amount:
                bill_amount = float(bill_amount.replace('$', '').replace(',', ''))
            years[bill_year] = {
                'bill': bill_amount
            }

        for row in response.xpath('//div[@id="assessedvaluehistory"]/div/table/tr'):
            year, assessed_value = row.xpath('td/text()').extract()
            year = int(year.strip())
            assessed_value = int(assessed_value.replace(',', ''))
            years[year]['assessment'] = assessed_value

        for row in response.xpath('//div[@id="taxratehistory"]/div/table/tr'):
            year, tax_rate = row.xpath('td/text()').extract()
            year = int(year.strip())
            tax_rate = float(tax_rate)
            years[year]['tax_rate'] = tax_rate

        tax_code_year = int(self.extract_with_prefix(response, 'taxCodeTaxYear')[1:5])
        tax_code = self.extract_with_prefix(response, 'propertyTaxCode')
        years[tax_code_year]['tax_code'] = tax_code

        item['tax_history'] = []
        for year, attrs in years.items():
            year_dict = dict(year=year)
            year_dict.update(attrs)
            item['tax_history'].append(year_dict)

        yield item
