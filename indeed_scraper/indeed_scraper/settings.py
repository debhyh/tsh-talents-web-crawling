import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["SCRAPEOPS_API_KEY"]

BOT_NAME = 'indeed_scraper'

SPIDER_MODULES = ['indeed_scraper.spiders']
NEWSPIDER_MODULE = 'indeed_scraper.spiders'

ROBOTSTXT_OBEY = False

# ScrapeOps API Key
SCRAPEOPS_API_KEY = API_KEY 

# Enable ScrapeOps Proxy
SCRAPEOPS_PROXY_ENABLED = True

# Add In The ScrapeOps Monitoring Extension
EXTENSIONS = {
'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}

DOWNLOADER_MIDDLEWARES = {

    ## ScrapeOps Monitor
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    
    ## Proxy Middleware
    'indeed_scraper.middlewares.ScrapeOpsProxyMiddleware': 725,
}

# Max Concurrency On ScrapeOps Proxy Free Plan is 1 thread
CONCURRENT_REQUESTS = 1