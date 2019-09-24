import scrapy
import re

class NationalCreditRegulatorSpider(scrapy.Spider):
    name = 'ncr'

    def __init__(self):
        self.storage_csv = 'data/credit-providers.csv'
        self.base_uri = 'https://www.ncr.org.za'

        self.registered_url =            '{}/register_of_registrants/registered_cp.php'.format(self.base_uri)
        self.voluntary_cancelled_url =   '{}/register_of_registrants/voluntary_cancelled_cp.php'.format(self.base_uri)
        self.cancelled_by_tribunal_url = '{}/register_of_registrants/cancelled_by_tribunal_cp1.php'.format(self.base_uri)
        self.lapsed_url =                '{}/register_of_registrants/lapsed_cp.php'.format(self.base_uri)

        f = open(self.storage_csv, 'w')
        f.write("credit_provider_name;trading_names;registration_status;effective_date")
        f.close()

        super().__init__()

    def start_requests(self):
        urls = [
            self.registered_url,
            self.voluntary_cancelled_url,
            self.cancelled_by_tribunal_url,
            self.lapsed_url
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        request_url = response.request.url

        with open(self.storage_csv, 'a') as f:
            output = response.css('div#output')

            # First two grid.grid-pad's are headers
            for grid in output.css('div.grid.grid-pad'):
                left_grid_table = grid.css('div.col-1-2')[0]

                # Credit provider name is in the 1st row, 2nd column
                credit_provider_name = left_grid_table.css('tr')[0].css('td::text')[1].extract()
                credit_provider_trading_names = None

                # Get trading names
                if self.lapsed_url in request_url:
                    credit_provider_trading_names = ''
                else:
                    try:
                        credit_provider_trading_names = left_grid_table.css('tr')[1].css('td::text')[1].extract()
                    except IndexError:
                        credit_provider_trading_names = ''

                # Set registration status
                registration_status = None

                if self.registered_url in request_url:
                    registration_status = 'registered'
                elif self.voluntary_cancelled_url in request_url:
                    registration_status = 'voluntarily_cancelled'
                elif self.cancelled_by_tribunal_url in request_url:
                    registration_status = 'cancelled_by_tribunal'
                elif self.lapsed_url in request_url:
                    registration_status = 'lapsed'

                # Get effective date aka registration, cancellation or lapsed date
                effective_date = None

                try:
                    if self.lapsed_url in request_url:
                        effective_date = left_grid_table.css('tr')[3].css('td::text')[1].extract()
                    else:
                        effective_date = left_grid_table.css('tr')[4].css('td::text')[1].extract()
                except IndexError:
                    effective_date = ''

                # Write row data to csv
                row_data = (credit_provider_name, credit_provider_trading_names, registration_status, effective_date)

                f.write('\n"%s";"%s";"%s";"%s"' % row_data)

        if response.css('a.navigation.next::attr(href)').extract_first() != 'javascript:void(0)':
            yield response.follow(response.css('a.navigation.next::attr(href)').extract_first(), self.parse)
