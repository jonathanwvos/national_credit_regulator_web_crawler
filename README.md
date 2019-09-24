# National Credit Regulator Web Scraper
The National Credit Regulator manages the registrations of financial service providers in South Africa. This includes:
* Credit Providers
* Credit Bureaus
* Debt Counsellors
* ADR Agents
* Payment Distribution Agencies

This repo stores a scrapy based web crawler to retrieve the registration status and trading names of active credit providers.

### Implementation
The scraper will recursively crawl each page of the NCR's Credit Provider Registrants and extract the official name, trading names, current registration status and the effective date of said status for each. If a request fails due to timeout, too many requests or for other reasons, the scraper will requeue it.

### Usage
scrapy runspider national_credit_regulator.py
